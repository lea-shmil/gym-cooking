(:requirements :adl :strips :typing :fluents)
(:types cell)
(:predicates
  (agent_at ?a - agent ?c - cell)
  (holding  ?a - agent ?o - object)
  (object_at ?o - object ?c - cell)
  (is_cut_board ?c - cell)
  (delivery_spot ?c - cell)
  (occupied ?c - cell)

  (adjacent? ?c1 - cell ?c2 - cell)
  (is_floor? ?c - cell)
  (holding_nothing? ?a - agent)
  (tomato? ?o - object)
  (lettuce? ?o - object)
  (plate? ?o - object)
  (chopped_lettuce? ?o - object)
  (chopped_tomato? ?o - object)
  (chopped_lettuce_on_plate? ?o - object)
  (chopped_tomato_on_plate? ?o - object)
  (salad? ?o - object)
  (salad_on_plate? ?o - object)
)



(:constants
  agent - agent
  object - object
)

; when agent moves how to make sure everything they carry moves?'
; can carry tomato, lettuce, plate, chopped lettuce, chopped tomato, chopped lettuce on a plate, chopped tomato on a plate
; can carry salad on place, salad

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

      (tomato? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
    )
)

(:action move-lettuce
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (lettuce? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
    )
)

(:action move-plate
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (plate? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
    )
)

(:action move-chopped-lettuce
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (chopped_lettuce? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
    )
)

(:action move-chopped-tomato
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (chopped_tomato? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
    )
)

(:action move-chopped-lettuce-on-plate
    :parameters (?a - agent ?start - cell ?end - cell ?obj1 - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj1)
      (chopped_lettuce_on_plate? ?obj1)

    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
    )
)

(:action move-chopped-tomato-on-plate
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (chopped_tomato_on_plate? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
    )
)

(:action move-salad
    :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?start)
      (adjacent? ?start ?end)
      (is_floor? ?end)
      (holding ?a ?obj)
      (salad? ?obj)
    )
    :effect (and
      (not (agent_at ?a ?start))
      (agent_at ?a ?end)
    )
)


(:action move-salad-on-plate
 :parameters (?a - agent ?start - cell ?end - cell ?obj - object)
 :precondition (and
   (agent_at ?a ?start)
   (adjacent? ?start ?end)
   (is_floor? ?end)
   (holding ?a ?obj)
   (salad_on_plate? ?obj1)
   )
  :effect (and
    (not (agent_at ?a ?start))
    (agent_at ?a ?end)
  )
)

; --------------------------------------------------------------------------------------------------------------------

; when chopping items are on cutting board
; when chopping cannot hold anything

(:action chop-tomato
    :parameters (?a - agent ?agent_loc - cell ?cut-board_loc - cell ?obj - object)
    :precondition (and
        (agent_at ?a ?agent_loc)
        (is_cut_board ?cut-board_loc)
        (tomato? ?obj)
        (object_at ?obj ?cut-board_loc)
        (adjacent? ?agent_loc ?cut-board_loc)
        (holding_nothing? ?a)
    )
    :effect (and
       (not (lettuce? ?obj))
       (chopped_lettuce? ?obj)
    )
)

(:action chop-lettuce
:parameters (?a - agent ?agent_loc - cell ?cut-board_loc - cell ?obj - object)
:precondition (and
    (agent_at ?a ?agent_loc)
    (is_cut_board ?cut-board_loc)
    (lettuce? ?obj)
    (object_at ?obj ?cut-board_loc)
    (adjacent? ?agent_loc ?cut-board_loc)
    (holding_nothing? ?a)
    )
:effect (and
    (not (lettuce? ?obj))
    (chopped_lettuce? ?obj)
    )
)

; --------------------------------------------------------------------------------------------------------------------

#can only pick stuff up if not holding anything
#otherwise puts both objects on shelf

(:action pickup-tomato
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (tomato? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
    (not (is-cutting-board ?obj_loc)) ; cannot pick up from cutting board
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing? ?a))
    )
)

(:action pickup-lettuce
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (lettuce? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
    (not (is-cutting-board ?obj_loc)) ; cannot pick up from cutting board
  )
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing? ?a))
  )
)

(:action pickup-plate
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (plate? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
  )
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing? ?a))
  )
)

(:action pickup-chopped-lettuce
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (chopped_lettuce? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
  )
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing? ?a))
  )
)

(:action pickup-chopped-tomato
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (chopped_tomato? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
  )
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing? ?a))
  )
)

(:action pickup-chopped-lettuce-on-plate
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (chopped_lettuce_on_plate? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
  )
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing? ?a))
  )
)

(:action pickup-chopped-tomato-on-plate
  :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (chopped_tomato_on_plate? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
  )
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing? ?a))
  )
)

(:action pickup-salad
    :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (salad? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
  )
  :effect (and
    (holding ?a ?obj)
    (not (object_at ?obj ?obj_loc))
    (not (holding_nothing? ?a))
  )
)

(:action pickup-salad-on-plate
    :parameters (?a - agent ?agent_loc - cell ?obj_loc - cell ?obj - object)
    :precondition (and
    (agent_at ?a ?agent_loc)
    (object_at ?obj ?obj_loc)
    (salad_on_plate? ?obj)
    (adjacent? ?agent_loc ?obj_loc)
    (holding_nothing? ?a)
    )
    :effect (and
      (holding ?a ?obj)
      (not (object_at ?obj ?obj_loc))
      (not (holding_nothing? ?a))
    )
)


; --------------------------------------------------------------------------------------------------------------------
; delivered objects are removed


(:action deliver-chopped-lettuce-on-plate
  :parameters (?a - agent ?agent_loc - cell ?delivery_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?obj)
    (chopped_lettuce_on-plate? ?obj)
    (deliver_spot ?delivery_loc)
    (adjacent? ?agent_loc ?delivery_loc)
  )
  :effect (and
    (delivered ?obj)
    (not (holding ?obj))
  )
)

(:action deliver-chopped-tomato-on-plate
  :parameters (?a - agent ?agent_loc - cell ?delivery_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?obj)
    (chopped_tomato_on_plate? ?obj)
    (deliver_spot ?delivery_loc)
    (adjacent? ?agent_loc ?delivery_loc)
  )
  :effect (and
    (delivered ?obj)
    (not (holding ?obj))
  )
)

(:action deliver-salad-on-plate
    :parameters (?a - agent ?agent_loc - cell ?delivery_loc - cell ?obj - object)
    :precondition (and
        (agent_at ?a ?agent_loc)
        (holding ?obj)
        (salad_on_plate? ?obj)
        (deliver_spot ?delivery_loc)
        (adjacent? ?agent_loc ?delivery_loc)
    )
    :effect (and
        (delivered ?obj)
        (not (holding ?obj))
    )
)


; --------------------------------------------------------------------------------------------------------------------

; when merging items are put down on the shelf
; can merge on cutting board loc
; cannot merge on delivery spot
; for now held object disappears and counter object is changed


(:action merge-chopped-tomato-plate
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?held_obj)
    (chopped_tomato? ?held_obj)
    (object_at ?counter_obj ?target_loc)
    (plate? ?counter_obj)
    (adjacent? ?agent_loc ?target_loc)
  )
  :effect (and
    (not (holding ?held_obj))
    (not (plate? ?counter_obj))
    (chopped_tomato_on_plate? ?counter_obj)
  )
)

(:action merge-plate-chopped-tomato
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
    :precondition (and
        (agent_at ?a ?agent_loc)
        (holding ?held_obj)
        (plate? ?held_obj)
        (object_at ?counter_obj ?target_loc)
        (chopped_tomato? ?counter_obj)
        (adjacent? ?agent_loc ?target_loc)
    )
    :effect (and
        (not (holding ?held_obj))
        (not (chopped_tomato? ?counter_obj))
        (chopped_tomato_on_plate? ?counter_obj)
    )

(:action merge-chopped-lettuce-plate
    :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
    :precondition (and
        (agent_at ?a ?agent_loc)
        (holding ?held_obj)
        (chopped_lettuce? ?held_obj)
        (object_at ?counter_obj ?target_loc)
        (plate? ?counter_obj)
        (adjacent? ?agent_loc ?target_loc)
    )
    :effect (and
        (not (holding ?held_obj))
        (not (plate? ?counter_obj))
        (chopped_lettuce_on_plate? ?counter-obj)
    )
)

(:action merge-plate-chopped-lettuce
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?held_obj)
    (plate? ?held_obj)
    (object_at ?counter_obj ?target_loc)
    (chopped_lettuce? ?counter_obj)
    (adjacent? ?agent_loc ?target_loc)
  )
  :effect (and
    (not (holding ?held_obj))
    (not (chopped_lettuce? ?counter_obj))
    (chopped_lettuce_on_plate? ?counter_obj
  )
)

(:action merge-salad-plate
    :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
    :precondition (and
        (agent_at ?a ?agent_loc)
        (holding ?held_obj)
        (salad? ?held_obj)
        (object_at ?counter_obj ?target_loc)
        (plate? ?counter_obj)
        (adjacent? ?agent_loc ?target_loc)
    )
    :effect (and
        (not (holding ?held_obj))
        (not (plate? ?counter_obj))
        (salad_on_plate? ?counter_obj)
    )
)

(:action merge-plate-salad
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?held_obj)
    (plate? ?held_obj)
    (object_at ?counter_obj ?target_loc)
    (salad? ?counter_obj)
    (adjacent? ?agent_loc ?target_loc)
  )
  :effect (and
    (not (holding ?held_obj))
    (not (salad? ?counter_obj))
    (salad_on_plate? ?counter_obj)
  )
)

(action merge-chopped-tomato-chopped-lettuce
    :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object?counter_obj - object)
    :precondition (and
        (agent_at ?a ?agent_loc)
        (holding ?held_obj)
        (chopped_tomato? ?held_obj)
        (object_at ?counter_obj ?target_loc)
        (chopped_lettuce? ?counter_obj)
        (adjacent? ?agent_loc ?target_loc)
    )
    :effect (and
        (not (holding ?held_obj))
        (not (chopped_lettuce? ?counter_obj))
        (salad? ?counter_obj)
    )
)

(:action merge-chopped-lettuce-chopped-tomato
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?held_obj - object ?counter_obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?held_obj)
    (chopped_lettuce? ?held_obj)
    (object_at ?counter_obj ?target_loc)
    (chopped_tomato? ?counter_obj)
    (adjacent? ?agent_loc ?target_loc)
  )
  :effect (and
    (not (holding ?held_obj))
    (not (chopped_tomato? ?counter_obj))
    (salad? ?counter_obj)
  )
)

; --------------------------------------------------------------------------------------------------------------------
; objects cannot be put down on delivery spot
; objects can be put on chopping board
; can put down any object

(:action put-down-tomato
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?obj)
    (not (occupied ?target_loc))
    (not (is_delivery ?target_loc))
    (adjacent? ?agent_loc ?target_loc)
    (tomato? ?obj)
  )
  :effect (and
    (not (holding ?obj))
    (object_at ?obj ?target_loc)
  )
)

(:action put-down-lettuce
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?obj)
    (not (occupied ?target_loc))
    (not (is_delivery ?target_loc))
    (adjacent? ?agent_loc ?target_loc)
    (lettuce? ?obj)
  )
  :effect (and
    (not (holding ?obj))
    (object_at ?obj ?target_loc)
  )
)

(:action put-down-plate
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?obj)
    (not (occupied ?target_loc))
    (not (is_delivery ?target_loc))
    (adjacent? ?agent_loc ?target_loc)
    (plate? ?obj)
  )
  :effect (and
    (not (holding ?obj))
    (object_at ?obj ?target_loc)
  )
)

(:action put-down-chopped-lettuce
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
  :precondition (and
    (agent_at ?a ?agent_loc)
    (holding ?obj)
    (not (occupied ?target_loc))
    (not (is_delivery ?target_loc))
    (adjacent? ?agent_loc ?target_loc)
    (chopped_lettuce? ?obj)
  )
  :effect (and
    (not (holding ?obj))
    (object_at ?obj ?target_loc)
  )
)

(:action put-down-chopped-tomato
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
    :precondition (and
        (agent_at ?a ?agent_loc)
        (holding ?obj)
        (not (occupied ?target_loc))
        (not (is_delivery ?target_loc))
        (adjacent? ?agent_loc ?target_loc)
        (chopped_tomato? ?obj)
    )
    :effect (and
        (not (holding ?obj))
        (object_at ?obj ?target_loc)
    )
)

(:action put-down-salad
  :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
    :precondition (and
        (agent_at ?a ?agent_loc)
        (holding ?obj)
        (not (occupied ?target_loc))
        (not (is_delivery ?target_loc))
        (adjacent? ?agent_loc ?target_loc)
        (salad? ?obj)
    )
    :effect (and
        (not (holding ?obj))
        (object_at ?obj ?target_loc)
    )
)

(:action put-down-chopped-tomato-on-plate
   :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?agent_loc)
      (holding ?obj)
      (not (occupied ?target_loc))
      (not (is_delivery ?target_loc))
      (adjacent? ?agent_loc ?target_loc)
      (chopped_tomato_on_plate? ?obj)
    )
    :effect (and
      (not (holding ?obj))
      (object_at ?obj ?target_loc)
    )
)

(:action put-down-chopped-lettuce-on-plate
    :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?agent_loc)
      (holding ?obj)
      (not (occupied ?target_loc))
      (not (is_delivery ?target_loc))
      (adjacent? ?agent_loc ?target_loc)
      (chopped_lettuce_on_plate? ?obj)
    )
    :effect (and
      (not (holding ?obj))
      (object_at ?obj ?target_loc)
    )
)

(:action put-down-salad-on-plate
    :parameters (?a - agent ?agent_loc - cell ?target_loc - cell ?obj - object)
    :precondition (and
      (agent_at ?a ?agent_loc)
      (holding ?obj)
      (not (occupied ?target_loc))
      (not (is_delivery ?target_loc))
      (adjacent? ?agent_loc ?target_loc)
      (salad_on_plate? ?obj)
    )
    :effect (and
      (not (holding ?obj))
      (object_at ?obj ?target_loc)
    )
)
