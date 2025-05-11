(define (domain ${instance_name})
	(:requirements :strips :typing :negative-preconditions :fluents) ${types}

	(:functions ${state_space}
	)
	(:predicates
		(game_over)
	) ${action_space}

	(:action a_game_over
		:parameters ()
		:precondition ()
		:effect ()
	)

)