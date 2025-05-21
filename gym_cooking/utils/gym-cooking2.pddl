(:requirements :adl :strips :typing :fluents)
(:types cell)
(:predicates
   (agent_at ?c - cell)
  (holding ?o - object)
  (object_at ?o - object ?c - cell)
  (is_cut-board ?c - cell)
  (needs_chop ?o - object)
  (is_chopped ?o - object)
  (is_deliverable ?o - object)
  (delivery_spot ?c - cell)
  (is_held ?o - object)
  (mergeable ?o1 - object ?o2 - object)
  (is_plate ?c - cell)
  (is_counter ?c - cell)
  (occupied ?c - cell)
  (is_delivery ?c - cell)
)
(:functions
  (x_cell ?c - cell)
  (y_cell ?c - cell)
  (cell_type ?c - cell)??
)

(:action move-north
  :parameters (?start - cell ?end - cell)
  :precondition (and (agent_at ?start)
  (= (y_cell ?start) (- (y_cell ?end) 1))
  (= (x_cell ?start) (x_cell ?end))
  (= (cell_type ?end) 0))
  :effect (and  (not (agent_at ?start)) (agent_at ?end) )
)

(:action move-south
  :parameters (?start - cell ?end - cell)
  :precondition (and (agent_at ?start)
    (= (y_cell ?start) (+ (y_cell ?end) 1))
    (= (x_cell ?start) (x_cell ?end))
    (= (cell_type ?end) 0)
  )
  :effect (and  (not (agent_at ?start)) (agent_at ?end))
)

(:action move-east
  :parameters (?start - cell ?end - cell)
  :precondition (and (agent_at ?start)
    (= (x_cell ?start) (- (x_cell ?end) 1))
    (= (y_cell ?start) (y_cell ?end))
    (= (cell_type ?end) 0)
  )
  :effect (and  (not (agent_at ?start)) (agent_at ?end))
)

(:action move-west
  :parameters (?start - cell ?end - cell)
  :precondition (and (agent_at ?start)
    (= (x_cell ?start) (+ (x_cell ?end) 1))
    (= (y_cell ?start) (y_cell ?end))
    (= (cell_type ?end) 0)
  )
  :effect (and  (not (agent_at ?start)) (agent_at ?end))
)

(:action chop-object
  :parameters (?agent_loc - cell ?cut-board_loc - cell ?obj - object)
  :precondition (and (agent_at ?agent_loc)
    (holding ?obj)
    (is_cut-board ?cut-board_loc)
    (needs_chop ?obj)
    (not (is_chopped ?obj))
    (or
      (and (=(x_cell ?agent_loc) (x_cell ?cut-board_loc)) (=(y_cell ?agent_loc) (- (y_cell ?cut-board_loc))1))
      (and (=(x_cell ?agent_loc) (x_cell ?cut-board_loc)) (=(y_cell ?agent_loc) (+ (y_cell ?cut-board_loc))1))
      (and (=(y_cell ?agent_loc) (y_cell ?cut-board_loc)) (=(x_cell ?agent_loc) (- (x_cell ?cut-board_loc))1))
      (and (=(y_cell ?agent_loc) (y_cell ?cut-board_loc)) (=(x_cell ?agent_loc) (+ (x_cell ?cut-board_loc))1))
    )
  )
  :effect (and
    (not (needs_chop ?obj))
    (is_chopped ?obj)
  )
)

(:action pickup-object
  :parameters (?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and(agent_at ?agent_loc)
    (not (delivery_spot ?obj_loc))
    (not (holding_anything))
    (object_at ?obj ?obj_loc)
    (not (is_held ?obj))
    (or
        (and (=(x_cell ?agent_loc) (x_cell ?obj_loc)) (=(y_cell ?agent_loc) (- (y_cell ?obj_loc))1))
        (and (=(x_cell ?agent_loc) (x_cell ?obj_loc)) (=(y_cell ?agent_loc) (+ (y_cell ?obj_loc))1))
        (and (=(y_cell ?agent_loc) (y_cell ?obj_loc)) (=(x_cell ?agent_loc) (- (x_cell ?obj_loc))1))
        (and (=(y_cell ?agent_loc) (y_cell ?obj_loc)) (=(x_cell ?agent_loc) (+ (x_cell ?obj_loc))1))
    )
    (or
      (and (is_cut-board ?obj_loc) (is_chopped ?obj))
      (not (is_cut-board ?obj_loc))
    )
  :effect (and
    (not (object_at ?obj ?obj_loc))
    (holding ?obj)
  )
)

(:action deliver-object
  :parameters (?agent_loc - cell ?delivery_loc - cell ?obj - object)
  :precondition (and (agent_at ?agent_loc)
    (holding ?obj)
    (is_deliverable ?obj)
    (deliver_spot ?delivery_loc)
    (or
     (and (=(x_cell ?agent_loc) (x_cell ?delivery_loc)) (=(y_cell ?agent_loc) (- (y_cell ?delivery_loc))1))
     (and (=(x_cell ?agent_loc) (x_cell ?delivery_loc)) (=(y_cell ?agent_loc) (+ (y_cell ?delivery_loc))1))
     (and (=(y_cell ?agente_loc) (y_cell ?delivery_loc)) (=(x_cell ?agent_loc) (- (x_cell ?delivery_loc))1))
     (and (=(y_cell ?agent_loc) (y_cell ?delivery_loc)) (=(x_cell ?agent_loc) (+ (x_cell ?delivery_loc))1))
    )
  )
  :effect (and
    (delivered ?obj)
    (not (holding ?obj))
    (increase (total_inventory) 1)
  )
)

(:action merge-objects
  :parameters (?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (agent_at ?agent_loc)
    (holding ?held_obj)
    (object_at ?counter_obj ?target_loc)
    (mergeable ?held_obj ?counter_obj)
    (or
      (and (=(x_cell ?agent_loc) (x_cell ?target_loc)) (=(y_cell ?agent_loc) (- (y_cell ?target_loc))1))
      (and (=(x_cell ?agent_loc) (x_cell ?target_loc)) (=(y_cell ?agent_loc) (+ (y_cell ?target_loc))1))
      (and (=(y_cell ?agent_loc) (y_cell ?target_loc)) (=(x_cell ?agent_loc) (- (x_cell ?target_loc))1))
      (and (=(y_cell ?agent_loc) (y_cell ?target_loc)) (=(x_cell ?agent_loc) (+ (x_cell ?target_loc))1))
    )
  )
  :effect (and
    (not (holding ?held_obj))
    (not (object_at ?counter_obj ?target_loc))
    (holding ?merged_obj) ;; assume merge result is predefined
  )
)


(:action put-down-object
  :parameters (?agent_loc - cell ?target_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?agent_loc)
    (holding ?obj)
    (not (occupied ?target_loc))
    (not (is_delivery ?target_loc))
    (or
      (and (=(x_cell ?agent_loc) (x_cell ?target_loc)) (=(y_cell ?agent_loc) (- (y_cell ?target_loc))1))
      (and (=(x_cell ?agent_loc) (x_cell ?target_loc)) (=(y_cell ?agent_loc) (+ (y_cell ?target_loc))1))
      (and (=(y_cell ?agent_loc) (y_cell ?target_loc)) (=(x_cell ?agent_loc) (- (x_cell ?target_loc))1))
      (and (=(y_cell ?agent_loc) (y_cell ?target_loc)) (=(x_cell ?agent_loc) (+ (x_cell ?target_loc))1))
    )
    (or
      (and (is_plate ?target_loc) (is_chopped ?obj))
      (is_counter ?target_loc)
    )
  )
  :effect (and
    (not (holding ?obj))
    (object_at ?obj ?target_loc)
  )
)
