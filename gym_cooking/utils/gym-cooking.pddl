(:requirements :adl :strips :typing :fluents)
(:types cell)
(:predicates
  (agent_at ?a - agent ?c - cell)
  (holding  ?a - agent ?o - object)
  (object_at ?o - object ?c - cell)
  (is_cut-board ?c - cell)
  (is_deliverable ?o - object)
  (delivery_spot ?c - cell)
  (is_held ?o - object)
  (mergeable ?o1 - object ?o2 - object)
  (is_counter ?c - cell)
  (occupied ?c - cell)
  (is_delivery ?c - cell)

  (adjacent? ?c1 - cell ?c2 - cell)
  (is_floor? ?c - cell)
  (holding_nothing? ?a - agent)
  (tomato? ?o - object)
  (lettuce? ?o - object)
  (plate? ?o - object)
  (chopped_lettuce? ?o - object)
  (chopped_tomato? ?o - object)

)


(:fluents
  (total_inventory)
)

(:constants
  agent - agent
  object - object
)

# when agent moves how to make sure everything they carry moves?'
#can carry tomato, lettuce, plate, chopped lettuce, chopped tomato, chopped lettuce on a plate, chopped tomato on a plate
#can carry salad on place, salad

(:action move
  :parameters (?a - agent ?start - cell ?end - cell)
  :precondition (and
  (agent_at ?a ?start)
  (adjacent? ?start ?end)
  (is_floor? ?end)
  (holding_nothing? ?a))

  :effect (and
  (not (agent_at ?a ?start))
  (agent_at ?a ?end) )
)

(:action move-tomato
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (object_at ?obj ?start)
      (tomato? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
       (not (object_at ?obj ?start))
      (object_at ?obj ?end)
    )

(:action move-lettuce
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (object_at ?obj ?start)
      (lettuce? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
       (not (object_at ?obj ?start))
      (object_at ?obj ?end)
    )
)

(:action move-plate
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (object_at ?obj ?start)
      (plate? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
       (not (object_at ?obj ?start))
      (object_at ?obj ?end)
    )
)

(:action move-chopped-lettuce
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (object_at ?obj ?start)
      (chopped_lettuce? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
       (not (object_at ?obj ?start))
      (object_at ?obj ?end)
    )
)

(:action move-chopped-tomato
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (object_at ?obj ?start)
      (chopped_tomato? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
       (not (object_at ?obj ?start))
      (object_at ?obj ?end)
    )
)

(:action move-chopped-lettuce-on-plate
    :parameters (?a - agent ?start - cell ?end - cell ?obj1 - object ?obj2 - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj1)
        (holding ?a ?obj2)
      (object_at ?obj1 ?start)
       (object_at ?obj2 ?start)
       (chopped_lettuce? ?obj1)
         (plate? ?obj2)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
       (not (object_at ?obj1 ?start))
      (object_at ?obj1 ?end)
         (not (object_at ?obj2 ?start))
        (object_at ?obj2 ?end)
    )
)

(:action move-chopped-tomato-on-plate
    :parameters (?a - agent ?start - cell ?end - cell ?obj1 - object ?obj2 - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj1)
      (holding ?a ?obj2)
      (object_at ?obj1 ?start)
       (object_at ?obj2 ?start)
       (chopped_tomato? ?obj1)
         (plate? ?obj2)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
      (not (object_at ?obj1 ?start))
      (object_at ?obj1 ?end)
      (not (object_at ?obj2 ?start))
      (object_at ?obj2 ?end)
    )
  )

  (:action move-salad
    :parameters (?a - agent ?start - cell ?end - cell ?obj1 - object obj2? - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj1)
      (holding ?a ?obj2)
      (object_at ?obj1 ?start)
      (object_at ?obj2 ?start)
      (chopped-lettuce? ?obj1)
      (chopped-tomato? ?obj2)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
      (not (object_at ?obj1 ?start))
      (object_at ?obj1 ?end)
      (not (object_at ?obj2 ?start))
      (object_at ?obj2 ?end)
    )
   )


   (:action move-salad-on-plate
     :parameters (?a - agent ?start - cell ?end - cell ?obj1 - object ?obj2 - object ?obj3 - object)
     :precondition (and
       (agent_at ?a ?start)
       (adjacent? ?start ?end)
       (is_floor? ?end)
       (holding ?a ?obj1)
       (holding ?a ?obj2)
       (holding ?a ?obj3)
       (object_at ?obj1 ?start)
       (object_at ?obj2 ?start)
       (object_at ?obj3 ?start)
       (chopped_lettuce? ?obj1)
       (chopped_tomato? ?obj2)
       (plate? ?obj3)
     )
        :effect (and
        (not (agent_at ?a ?start))
        (agent_at ?a ?end)
        (not (object_at ?obj1 ?start))
        (object_at ?obj1 ?end)
        (not (object_at ?obj2 ?start))
        (object_at ?obj2 ?end)
        (not (object_at ?obj3 ?start))
        (object_at ?obj3 ?end)
        )


(:action chop-tomato
:parameters (?a - agent ?agent_loc - cell ?cut-board_loc - cell ?obj - object)
:precondition (and
  (agent_at ?a ?agent_loc)
  (holding ?obj)
  (is_cut-board ?cut-board_loc)
  (tomato? ?obj)
  (adjacent? ?agent_loc ?cut-board_loc)
  )
:effect (and
    (is_chopped ?obj)
    (not (tomato? ?obj))
    (chopped_tomato? ?obj)
    (object_at ?obj ?cut-board_loc)
    )
  )

    (:action chop-lettuce


(:action pickup-object
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and (agent_at ?a ?agent_loc)
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
  :parameters (?a - agent ?agent_loc - cell ?delivery_loc - cell ?obj - object)
  :precondition (and (agent_at ?a ?agent_loc)
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
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
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
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
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
