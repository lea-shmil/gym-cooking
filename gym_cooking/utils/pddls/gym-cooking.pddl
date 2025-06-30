(define (domain grid_overcooked)
(:requirements :adl :strips :typing :conditional-effects :negative-preconditions)
(:types cell agent object)
  ; cell is a type for the grid cells
  ; agent is a type for the agent that performs actions
  ; object is a type for the objects in the environment (e.g., tomato, lettuce, plate)


(:predicates
  (agent_at ?a - agent ?c - cell)
  (holding  ?a - agent ?o - object)
  (object_at ?o - object ?c - cell)
  (is_cutting_board ?c - cell)
  (delivery_spot ?c - cell)
  (occupied ?c - cell)
  (adjacent ?c1 - cell ?c2 - cell)
  (is_floor ?c - cell)
  (holding_nothing ?a - agent)
  (tomato ?o - object)
  (lettuce ?o - object)
  (plate ?o - object)
  (not-plate ?o - object) ; for objects that are not plates
  (chopped ?o - object)
  (delivered ?o - object)
)

; when agent moves how to make sure everything they carry moves?'
; can carry tomato, lettuce, plate, chopped lettuce, chopped tomato, chopped lettuce on a plate, chopped tomato on a plate
; can carry salad on place, salad

(:action move
  :parameters (?a - agent ?start - cell ?end - cell)
  :precondition (and
  (agent_at ?a ?start)
  (adjacent ?start ?end)
  (is_floor ?end)
  (not (occupied ?end)) ; cannot move to an occupied cell
  )
  :effect (and
  (not (agent_at ?a ?start))
  (agent_at ?a ?end)
  (occupied ?end) ; mark the new cell as occupied
  (not (occupied ?start)) ; mark the old cell as not occupied
  )
)


; --------------------------------------------------------------------------------------------------------------------

; when chopping items are being held


(:action chop
    :parameters (?a - agent ?agent_loc - cell ?cut-board_loc - cell ?obj - object)
    :precondition (and
        (not-plate ?obj) ; cannot chop a plate
        (not (plate ?obj)) ; cannot chop a plate
        (agent_at ?a ?agent_loc)
        (is_cutting_board ?cut-board_loc)
        (not (chopped ?obj)) ; cannot chop if already chopped
        (holding ?a ?obj) ; must be holding the object to chop
        (adjacent ?agent_loc ?cut-board_loc)
        (not (occupied ?cut-board_loc)) ; cannot chop on an occupied cutting board
    )
    :effect
        (and (chopped ?obj))

)


; --------------------------------------------------------------------------------------------------------------------

; can only pick stuff up if not holding anything
; otherwise puts both objects on shelf

(:action pickup
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (adjacent ?agent_loc ?obj_loc)
    (holding_nothing  ?a)
    )
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing  ?a))
    (not (occupied ?obj_loc)) ; mark the cell as not occupied after picking up the object
    )
)



; --------------------------------------------------------------------------------------------------------------------
; delivered objects are removed


(:action deliver
  :parameters (?a - agent ?agent_loc - cell ?delivery_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?a ?obj)
    (not (not-plate ?obj)) ; can deliver only a plated object
    (chopped ?obj)
    (delivery_spot ?delivery_loc)
    (adjacent ?agent_loc ?delivery_loc)
  )
  :effect (and
    (delivered ?obj)
    (not (holding ?a ?obj))
    (holding_nothing ?a)
  )
)


; --------------------------------------------------------------------------------------------------------------------

; when merging items are put down on the shelf
; can merge on cutting board loc
; cannot merge on delivery spot
; for now held object disappears and counter object is changed


(:action merge-plate    ; for putting salad, chopped lettuce, chopped tomato
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (not-plate ?counter_obj) ; cannot merge plate with plate
    (agent_at ?a ?agent_loc)
    (holding ?a ?held_obj)
    (plate ?held_obj)
    (object_at ?counter_obj ?target_loc)
    (occupied ?target_loc) ; the target location must be occupied by the counter object
    (adjacent ?agent_loc ?target_loc)
    (chopped ?counter_obj) ; cannot merge plate with tomato/lettuce
  )
  :effect (and
    (not (not-plate ?counter_obj)) ; the counter object now becomes a plate
    (not (holding ?a ?held_obj))
    (holding ?a ?counter_obj) ; now holding the counter object
    (not (object_at ?counter_obj ?target_loc)) ; remove the counter object from its previous location
    (not (occupied ?target_loc)) ; mark the cell as not occupied after merging
  )
)

(:action merge-plate-on-counter    ; for putting salad, chopped lettuce, chopped tomato
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?a ?held_obj)
    (plate ?counter_obj)
    (object_at ?counter_obj ?target_loc)
    (adjacent ?agent_loc ?target_loc)
    (chopped ?held_obj) ; cannot merge plate with tomato/lettuce
    (not-plate ?held_obj) ; cannot merge plate with plate
    (occupied ?target_loc)
  )
  :effect (and
    (not (not-plate ?held_obj)) ; the held object now becomes a plate
    (not (object_at ?counter_obj ?target_loc))
    (not (occupied ?target_loc)) ; mark the cell as not occupied after merging
  )
)

(:action merge-no-plate ; for putting chopped lettuce with chopped tomato
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?a ?held_obj)
    (object_at ?counter_obj ?target_loc)
    (adjacent ?agent_loc ?target_loc)
    (chopped ?held_obj) ; cannot merge plate with tomato/lettuce
    (chopped ?counter_obj) ; cannot merge plate with tomato/lettuce
    (not-plate ?held_obj) ; cannot merge plate with plate
    (not-plate ?counter_obj) ; cannot merge plate with plate
    (occupied ?target_loc)
  )
  :effect (and
    (not (object_at ?counter_obj ?target_loc))
    (not (occupied ?target_loc)) ; mark the cell as not occupied after merging
    (tomato ?held_obj)
    (lettuce ?held_obj)
  )
)


; --------------------------------------------------------------------------------------------------------------------


; objects cannot be put down on delivery spot
; objects can be put on chopping board
; can put down any object

(:action put-down
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?a ?obj)
    (not (occupied ?target_loc))
    (not (delivery_spot ?target_loc))
    (not (is_floor ?target_loc)) ; cannot put down on floor
    (adjacent ?agent_loc ?target_loc)
    (or (not (is_cutting_board ?target_loc)) ; can put down on cutting board
        (plate ?obj) ; can put down a plate
        (not (not-plate ?obj))
        (chopped ?obj) ; can put down a chopped object
    )
    )
  :effect (and
    (not (holding ?a ?obj))
    (object_at ?obj ?target_loc)
    (holding_nothing  ?a)
    (occupied ?target_loc)
  )
)

)