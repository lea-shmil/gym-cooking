(define (problem ${instance_name})
	(:domain ${domain_name}) ${objects}

	(:init ${initial_state}
	)

	(:goal
		(and ${goal_state} (not (game_over))
		)
	)
	(:metric maximize(r0)
	)
)