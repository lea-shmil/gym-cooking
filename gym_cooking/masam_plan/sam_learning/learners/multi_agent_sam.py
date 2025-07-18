"""Module to learn action models from multi-agent trajectories with joint actions."""
import logging
from io import StringIO
from typing import Dict, List, Tuple, Set, Optional

from pddl_plus_parser.models import (
    Predicate,
    Domain,
    MultiAgentComponent,
    MultiAgentObservation,
    ActionCall,
    State,
    GroundedPredicate,
    JointActionCall,
)

from gym_cooking.masam_plan.sam_learning.core.learner_domain import LearnerDomain , LearnerAction
from gym_cooking.masam_plan.sam_learning.core.matching_utils import  extract_discrete_effects
from gym_cooking.masam_plan.sam_learning.core.propositional_operations.literals_cnf import LiteralCNF
from gym_cooking.masam_plan.sam_learning.core.propositional_operations.discrete_utilities import extract_predicate_data
from gym_cooking.masam_plan.sam_learning.learners.sam_learning import SAMLearner
from gym_cooking.masam_plan.utilities.util_types import NegativePreconditionPolicy


class MultiAgentSAM(SAMLearner):
    """Class designated to learning action models from multi-agent trajectories with joint actions."""

    logger: logging.Logger

    literals_cnf: Dict[str, LiteralCNF]
    preconditions_fluent_map: Dict[str, List[str]]
    safe_actions: List[str]

    def __init__(
            self,
            partial_domain: Domain,
            preconditions_fluent_map: Optional[Dict[str, List[str]]] = None,
            negative_precondition_policy: NegativePreconditionPolicy = NegativePreconditionPolicy.no_remove,
    ):
        super().__init__(partial_domain, negative_preconditions_policy=negative_precondition_policy)
        self.logger = logging.getLogger(__name__)
        self.literals_cnf = {}
        self.preconditions_fluent_map = preconditions_fluent_map if preconditions_fluent_map else {}
        self.safe_actions = []
        self._unsafe_actions = set()


        self.logger = logging.getLogger(__name__)  # Properly initialize the logger
        self.log_stream = StringIO()  # Create a StringIO object to capture logs
        stream_handler = logging.StreamHandler(self.log_stream)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.DEBUG)  # Set


    def _initialize_cnfs(self) -> None:
        """Initialize the CNFs for the action model."""
        self.logger.debug("Initializing CNFs for the action model.")
        for predicate in self.partial_domain.predicates.values():
            self.literals_cnf[predicate.untyped_representation] = LiteralCNF(action_names=list(self.partial_domain.actions.keys()))
            negative_predicate = Predicate(name=predicate.name, signature=predicate.signature, is_positive=False)
            self.literals_cnf[negative_predicate.untyped_representation] = LiteralCNF(action_names=list(self.partial_domain.actions.keys()))

    def _extract_relevant_not_effects(self, executing_actions: List[ActionCall], relevant_action: ActionCall,) -> List[GroundedPredicate]:
        """Extracts the literals that cannot be an effect of the relevant action.

        :param executing_actions: the actions that are being executed in the joint action triplet.
        :param relevant_action: the current action that is being tested.
        :return: the literals that cannot be effects of the action.
        """
        not_in_state_predicates = []
        # creating the complementary group of predicates from the next state.
        for predicate in self.triplet_snapshot.next_state_predicates:
            not_in_state_predicates.append(
                GroundedPredicate(
                    name=predicate.name, signature=predicate.signature, object_mapping=predicate.object_mapping, is_positive=not predicate.is_positive
                )
            )

        combined_not_effects = []
        # extracting the state predicates that cannot be effects of the action.
        for predicate in not_in_state_predicates:
            interacting_actions = self.compute_interacting_actions(predicate, executing_actions)
            if relevant_action not in interacting_actions:
                continue

            combined_not_effects.append(predicate)

        return combined_not_effects

    def _is_action_safe(self, action: LearnerAction, preconditions_to_filter: Set[Predicate]) -> bool:
        """Checks if the given action is safe to execute.

        :param action: the lifted action that is to be learned.
        :return: whether the action is safe to execute.
        """
        for domain_literal, cnf in self.literals_cnf.items():
            if not cnf.is_action_acting_in_cnf(action.name):
                self.logger.debug(f"The literal {domain_literal} does not relate to {action.name}.")
                continue

            action_preconditions = {p.untyped_representation for p in preconditions_to_filter}
            if not cnf.is_action_safe(action_name=action.name, action_preconditions=action_preconditions):
                self.logger.debug("Action %s is not safe to execute!", action.name)
                return False

        return True

    def add_not_effect_to_cnf(self, executed_action: ActionCall, not_effects: List[GroundedPredicate]) -> None:
        """Adds a predicate that cannot be an action's effect to the correct CNF.

        :param executed_action: the action that is being executed in the current joint action triplet.
        :param not_effects: the predicates that cannot be the effects of the action.
        """
        for predicate in not_effects:
            bounded_lifted_literal = self.matcher.get_injective_match(predicate, executed_action)
            if bounded_lifted_literal is None:
                continue

            self.literals_cnf[predicate.lifted_untyped_representation].add_not_effect(executed_action.name, bounded_lifted_literal)
            self.logger.debug(f"Removing the literal from being an effect of the action {executed_action.name}.")

    def add_must_be_effect_to_cnf(self, executed_action: ActionCall, grounded_effects: Set[GroundedPredicate]) -> None:
        """Adds an effect that has no ambiguities on which action caused it.

        :param executed_action: the action that caused the effect.
        :param grounded_effects: the grounded predicate that is affected by the action.
        """
        self.logger.info("Adding the effects that contain no ambiguity to the CNF.")
        for grounded_literal in grounded_effects:
            lifted_effect = self.matcher.get_injective_match(grounded_literal, executed_action)
            if lifted_effect is None:
                continue

            self.literals_cnf[grounded_literal.lifted_untyped_representation].add_possible_effect(
                [(executed_action.name, lifted_effect.untyped_representation)]
            )

    def compute_interacting_actions(self, grounded_predicate: GroundedPredicate, executing_actions: List[ActionCall]):
        """Computes the set of actions that interact with a certain predicate.

        :param grounded_predicate: the effect predicate that is being interacted by possibly more than one action.
        :param executing_actions: the actions that are being executed in the joint action.
        :return: the actions that interact with the predicate.
        """
        self.logger.debug(f"Computing the set of actions that interact with predicate " f"{grounded_predicate.untyped_representation}.")
        interacting_actions = []
        for action in executing_actions:
            action_parameters = action.parameters
            action_parameters.extend(self.partial_domain.constants.keys())
            predicate_parameters = set(grounded_predicate.grounded_objects)
            if predicate_parameters.issubset(action_parameters):
                interacting_actions.append(action)

        self.logger.debug(
            f"The actions {[str(action) for action in interacting_actions]} "
            f"interact with the predicate {grounded_predicate.untyped_representation}"
        )
        return interacting_actions

    def extract_effects_from_cnf(self, action: LearnerAction, relevant_preconditions: Set[Predicate]) -> None:
        """Extracts the action's relevant effects from the CNF object.

        :param action: the action that is currently being handled.
        :param relevant_preconditions: the preconditions of the action to filter the possible effects from.
        """
        relevant_preconditions_str = {predicate.untyped_representation for predicate in relevant_preconditions}
        for domain_predicate, cnf in self.literals_cnf.items():
            cnf_effects = cnf.extract_action_effects(action.name, relevant_preconditions_str)
            for effect in cnf_effects:
                lifted_predicate = extract_predicate_data(action.signature, effect, self.partial_domain.constants)
                action.discrete_effects.add(lifted_predicate)

    def handle_concurrent_execution(self, grounded_effect: GroundedPredicate, executing_actions: List[ActionCall]) -> None:
        """Handles the case where effects can be achieved from more than one action.

        :param grounded_effect: the effect that is being targeted by more than one action.
        :param executing_actions: the actions that are part of the joint action.
        """
        self.logger.info("Handling concurrent execution of actions.")
        interacting_actions = self.compute_interacting_actions(grounded_effect, executing_actions)
        if len(interacting_actions) == 1:
            self.add_must_be_effect_to_cnf(interacting_actions[0], {grounded_effect})
            return

        concurrent_execution = []
        for interacting_action in interacting_actions:
            lifted_match = self.matcher.get_injective_match(grounded_effect, interacting_action)
            concurrent_execution.append((interacting_action.name, lifted_match.untyped_representation))

        self.literals_cnf[grounded_effect.lifted_untyped_representation].add_possible_effect(concurrent_execution)

    def update_single_agent_executed_action(self, executed_action: ActionCall) -> None:
        """Handles the situations where only one agent executed an action in a joint action.

        :param executed_action: the single operational action in the joint action.
        """
        self.logger.info(f"Handling the execution of the single action - {str(executed_action)}.")
        observed_action = self.partial_domain.actions[executed_action.name]
        if executed_action.name not in self.observed_actions:
            super()._add_new_action_preconditions(executed_action)
            self.observed_actions.append(observed_action.name)

        else:
            super()._update_action_preconditions(executed_action)

        grounded_add_effects, grounded_del_effects = extract_discrete_effects(
            self.triplet_snapshot.previous_state_predicates, self.triplet_snapshot.next_state_predicates
        )
        self.logger.debug("Updating the literals that must be effects of the action.")
        self.add_must_be_effect_to_cnf(executed_action, grounded_add_effects.union(grounded_del_effects))
        not_effects = self._extract_relevant_not_effects(executing_actions=[executed_action], relevant_action=executed_action,)
        self.add_not_effect_to_cnf(executed_action, not_effects)

    def update_multiple_executed_actions(self, joint_action: JointActionCall, previous_state: State, next_state: State) -> None:
        """Handles the case where more than one action is executed in a single trajectory triplet.

        :param joint_action: the joint action that was executed.
        :param previous_state: the state prior to the joint action's execution.
        :param next_state: the state following the joint action's execution.
        """
        self.logger.info("Learning when multiple actions are executed concurrently.")
        executing_actions = joint_action.operational_actions
        for executed_action in executing_actions:
            observed_action = self.partial_domain.actions[executed_action.name]
            self.triplet_snapshot.create_triplet_snapshot(
                previous_state=previous_state,
                next_state=next_state,
                current_action=executed_action,
                observation_objects=self.current_trajectory_objects,
            )
            if executed_action.name not in self.observed_actions:
                super()._add_new_action_preconditions(executed_action)
                self.observed_actions.append(observed_action.name)

            else:
                super()._update_action_preconditions(executed_action)

        grounded_add_effects, grounded_del_effects = extract_discrete_effects(
            self.triplet_snapshot.previous_state_predicates, self.triplet_snapshot.next_state_predicates
        )
        for executed_action in executing_actions:
            not_effects = self._extract_relevant_not_effects(executing_actions=[executed_action], relevant_action=executed_action,)
            self.add_not_effect_to_cnf(executed_action, not_effects)

        for grounded_effect in grounded_add_effects.union(grounded_del_effects):
            self.handle_concurrent_execution(grounded_effect, executing_actions)

    def handle_multi_agent_trajectory_component(self, component: MultiAgentComponent) -> None:
        """Handles a single multi-agent triplet in the observed trajectory.

        :param component: the triplet to handle.
        """
        previous_state = component.previous_state
        joint_action = component.grounded_joint_action
        next_state = component.next_state

        if any([self._verify_parameter_duplication(action) for action in joint_action.operational_actions]):
            self.logger.warning(f"{str(joint_action)} contains duplicated parameters! Not suppoerted in SAM.")
            return

        if joint_action.action_count == 1:
            executing_action = joint_action.operational_actions[0]
            self.triplet_snapshot.create_triplet_snapshot(
                previous_state=previous_state,
                next_state=next_state,
                current_action=executing_action,
                observation_objects=self.current_trajectory_objects,
            )
            self.update_single_agent_executed_action(executing_action)
            return

        self.logger.debug("More than one action is being executed in the current triplet.")
        self.update_multiple_executed_actions(joint_action, previous_state, next_state)

    def construct_safe_actions(self, should_remove_actions: bool = True) -> None:
        """Constructs the single-agent actions that are safe to execute.

        :param should_remove_actions: whether to remove the actions that are not safe to execute. (for MA-SAM+)
        """
        super()._remove_unobserved_actions_from_partial_domain()
        for action in self.partial_domain.actions.values():
            self.logger.debug("Constructing safe action for %s", action.name)
            action_preconditions = {precondition for precondition in action.preconditions.root.operands if isinstance(precondition, Predicate)}
            if not self._is_action_safe(action, action_preconditions):
                self.logger.warning("Action %s is not safe to execute!", action.name)
                self._unsafe_actions.add(action.name)
                continue

            self.logger.debug("Action %s is safe to execute.", action.name)
            self.safe_actions.append(action.name)
            self.extract_effects_from_cnf(action, action_preconditions)

        if should_remove_actions:
            for unsafe_action in self._unsafe_actions:
                self.partial_domain.actions.pop(unsafe_action)

    def learn_combined_action_model(self, observations: List[MultiAgentObservation]) -> Tuple[LearnerDomain, Dict[str, str]]:
        """Learn the SAFE action model from the input multi-agent trajectories.

        :param observations: the multi-agent observations.
        :return: a domain containing the actions that were learned.
        """
        self.logger.info("Starting to learn the action model!")
        super().start_measure_learning_time()
        self._initialize_cnfs()

        super().deduce_initial_inequality_preconditions()
        for observation in observations:
            self.current_trajectory_objects = observation.grounded_objects
            for component in observation.components:
                self.handle_multi_agent_trajectory_component(component)

        self.construct_safe_actions()
        self.handle_negative_preconditions_policy()
        self.logger.info("Finished learning the action model!")
        super().end_measure_learning_time()
        learning_report = super()._construct_learning_report()
        return self.partial_domain, learning_report

    def print_logs(self):
        """Print the captured logs."""
        print(self.log_stream.getvalue())