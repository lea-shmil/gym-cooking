; PDDL file for map2_tomato_v2
(define (problem map2_tomato_v2)
(:domain grid_overcooked)

(:objects
    x0y0 - cell
    x0y1 - cell
    x0y2 - cell
    x0y3 - cell
    x0y4 - cell
    x0y5 - cell
    x0y6 - cell
    x0y7 - cell
    x0y8 - cell
    x0y9 - cell
    x1y0 - cell
    x1y1 - cell
    x1y2 - cell
    x1y3 - cell
    x1y4 - cell
    x1y5 - cell
    x1y6 - cell
    x1y7 - cell
    x1y8 - cell
    x1y9 - cell
    x2y0 - cell
    x2y1 - cell
    x2y2 - cell
    x2y3 - cell
    x2y4 - cell
    x2y5 - cell
    x2y6 - cell
    x2y7 - cell
    x2y8 - cell
    x2y9 - cell
    x3y0 - cell
    x3y1 - cell
    x3y2 - cell
    x3y3 - cell
    x3y4 - cell
    x3y5 - cell
    x3y6 - cell
    x3y7 - cell
    x3y8 - cell
    x3y9 - cell
    x4y0 - cell
    x4y1 - cell
    x4y2 - cell
    x4y3 - cell
    x4y4 - cell
    x4y5 - cell
    x4y6 - cell
    x4y7 - cell
    x4y8 - cell
    x4y9 - cell
    x5y0 - cell
    x5y1 - cell
    x5y2 - cell
    x5y3 - cell
    x5y4 - cell
    x5y5 - cell
    x5y6 - cell
    x5y7 - cell
    x5y8 - cell
    x5y9 - cell
    x6y0 - cell
    x6y1 - cell
    x6y2 - cell
    x6y3 - cell
    x6y4 - cell
    x6y5 - cell
    x6y6 - cell
    x6y7 - cell
    x6y8 - cell
    x6y9 - cell
    x7y0 - cell
    x7y1 - cell
    x7y2 - cell
    x7y3 - cell
    x7y4 - cell
    x7y5 - cell
    x7y6 - cell
    x7y7 - cell
    x7y8 - cell
    x7y9 - cell
    a1 - agent
    a2 - agent
    o0 - veggieOrPlate
    o1 - veggieOrPlate
    o2 - veggieOrPlate
    o3 - veggieOrPlate
    o4 - veggieOrPlate
    o5 - veggieOrPlate
    o6 - veggieOrPlate
)

(:init
(agent_at a1 x1y5)(holding_nothing a1)(occupied x1y5)(agent_at a2 x4y4)(holding_nothing a2)(occupied x4y4)(adjacent x0y0 x1y0)(adjacent x1y0 x0y0)(adjacent x0y0 x0y1)(adjacent x0y1 x0y0)(adjacent x1y0 x2y0)(adjacent x2y0 x1y0)(adjacent x1y0 x1y1)(adjacent x1y1 x1y0)(adjacent x2y0 x3y0)(adjacent x3y0 x2y0)(adjacent x2y0 x2y1)(adjacent x2y1 x2y0)(adjacent x3y0 x4y0)(adjacent x4y0 x3y0)(adjacent x3y0 x3y1)(adjacent x3y1 x3y0)(adjacent x4y0 x5y0)(adjacent x5y0 x4y0)(adjacent x4y0 x4y1)(adjacent x4y1 x4y0)(adjacent x5y0 x6y0)(adjacent x6y0 x5y0)(adjacent x5y0 x5y1)(adjacent x5y1 x5y0)(adjacent x6y0 x7y0)(adjacent x7y0 x6y0)(adjacent x6y0 x6y1)(adjacent x6y1 x6y0)(adjacent x7y0 x7y1)(adjacent x7y1 x7y0)(adjacent x0y1 x1y1)(adjacent x1y1 x0y1)(adjacent x0y1 x0y2)(adjacent x0y2 x0y1)(is_floor x1y1)(adjacent x1y1 x2y1)(adjacent x2y1 x1y1)(adjacent x1y1 x1y2)(adjacent x1y2 x1y1)(adjacent x2y1 x3y1)(adjacent x3y1 x2y1)(adjacent x2y1 x2y2)(adjacent x2y2 x2y1)(is_floor x3y1)(adjacent x3y1 x4y1)(adjacent x4y1 x3y1)(adjacent x3y1 x3y2)(adjacent x3y2 x3y1)(is_floor x4y1)(adjacent x4y1 x5y1)(adjacent x5y1 x4y1)(adjacent x4y1 x4y2)(adjacent x4y2 x4y1)(adjacent x5y1 x6y1)(adjacent x6y1 x5y1)(adjacent x5y1 x5y2)(adjacent x5y2 x5y1)(is_floor x6y1)(adjacent x6y1 x7y1)(adjacent x7y1 x6y1)(adjacent x6y1 x6y2)(adjacent x6y2 x6y1)(adjacent x7y1 x7y2)(adjacent x7y2 x7y1)(adjacent x0y2 x1y2)(adjacent x1y2 x0y2)(adjacent x0y2 x0y3)(adjacent x0y3 x0y2)(is_floor x1y2)(adjacent x1y2 x2y2)(adjacent x2y2 x1y2)(adjacent x1y2 x1y3)(adjacent x1y3 x1y2)(is_floor x2y2)(adjacent x2y2 x3y2)(adjacent x3y2 x2y2)(adjacent x2y2 x2y3)(adjacent x2y3 x2y2)(adjacent x3y2 x4y2)(adjacent x4y2 x3y2)(adjacent x3y2 x3y3)(adjacent x3y3 x3y2)(is_floor x4y2)(adjacent x4y2 x5y2)(adjacent x5y2 x4y2)(adjacent x4y2 x4y3)(adjacent x4y3 x4y2)(is_floor x5y2)(adjacent x5y2 x6y2)(adjacent x6y2 x5y2)(adjacent x5y2 x5y3)(adjacent x5y3 x5y2)(adjacent x6y2 x7y2)(adjacent x7y2 x6y2)(adjacent x6y2 x6y3)(adjacent x6y3 x6y2)(adjacent x7y2 x7y3)(adjacent x7y3 x7y2)(adjacent x0y3 x1y3)(adjacent x1y3 x0y3)(adjacent x0y3 x0y4)(adjacent x0y4 x0y3)(is_cutting_board x1y3)(adjacent x1y3 x2y3)(adjacent x2y3 x1y3)(adjacent x1y3 x1y4)(adjacent x1y4 x1y3)(is_floor x2y3)(adjacent x2y3 x3y3)(adjacent x3y3 x2y3)(adjacent x2y3 x2y4)(adjacent x2y4 x2y3)(is_floor x3y3)(adjacent x3y3 x4y3)(adjacent x4y3 x3y3)(adjacent x3y3 x3y4)(adjacent x3y4 x3y3)(is_floor x4y3)(adjacent x4y3 x5y3)(adjacent x5y3 x4y3)(adjacent x4y3 x4y4)(adjacent x4y4 x4y3)(is_floor x5y3)(adjacent x5y3 x6y3)(adjacent x6y3 x5y3)(adjacent x5y3 x5y4)(adjacent x5y4 x5y3)(is_floor x6y3)(adjacent x6y3 x7y3)(adjacent x7y3 x6y3)(adjacent x6y3 x6y4)(adjacent x6y4 x6y3)(adjacent x7y3 x7y4)(adjacent x7y4 x7y3)(adjacent x0y4 x1y4)(adjacent x1y4 x0y4)(adjacent x0y4 x0y5)(adjacent x0y5 x0y4)(is_floor x1y4)(adjacent x1y4 x2y4)(adjacent x2y4 x1y4)(adjacent x1y4 x1y5)(adjacent x1y5 x1y4)(adjacent x2y4 x3y4)(adjacent x3y4 x2y4)(adjacent x2y4 x2y5)(adjacent x2y5 x2y4)(is_floor x3y4)(adjacent x3y4 x4y4)(adjacent x4y4 x3y4)(adjacent x3y4 x3y5)(adjacent x3y5 x3y4)(is_floor x4y4)(adjacent x4y4 x5y4)(adjacent x5y4 x4y4)(adjacent x4y4 x4y5)(adjacent x4y5 x4y4)(is_floor x5y4)(adjacent x5y4 x6y4)(adjacent x6y4 x5y4)(adjacent x5y4 x5y5)(adjacent x5y5 x5y4)(is_floor x6y4)(adjacent x6y4 x7y4)(adjacent x7y4 x6y4)(adjacent x6y4 x6y5)(adjacent x6y5 x6y4)(adjacent x7y4 x7y5)(adjacent x7y5 x7y4)(adjacent x0y5 x1y5)(adjacent x1y5 x0y5)(adjacent x0y5 x0y6)(adjacent x0y6 x0y5)(is_floor x1y5)(adjacent x1y5 x2y5)(adjacent x2y5 x1y5)(adjacent x1y5 x1y6)(adjacent x1y6 x1y5)(delivery_spot x2y5)(adjacent x2y5 x3y5)(adjacent x3y5 x2y5)(adjacent x2y5 x2y6)(adjacent x2y6 x2y5)(adjacent x3y5 x4y5)(adjacent x4y5 x3y5)(adjacent x3y5 x3y6)(adjacent x3y6 x3y5)(is_floor x4y5)(adjacent x4y5 x5y5)(adjacent x5y5 x4y5)(adjacent x4y5 x4y6)(adjacent x4y6 x4y5)(is_floor x5y5)(adjacent x5y5 x6y5)(adjacent x6y5 x5y5)(adjacent x5y5 x5y6)(adjacent x5y6 x5y5)(is_floor x6y5)(adjacent x6y5 x7y5)(adjacent x7y5 x6y5)(adjacent x6y5 x6y6)(adjacent x6y6 x6y5)(adjacent x7y5 x7y6)(adjacent x7y6 x7y5)(adjacent x0y6 x1y6)(adjacent x1y6 x0y6)(adjacent x0y6 x0y7)(adjacent x0y7 x0y6)(is_floor x1y6)(adjacent x1y6 x2y6)(adjacent x2y6 x1y6)(adjacent x1y6 x1y7)(adjacent x1y7 x1y6)(is_cutting_board x2y6)(adjacent x2y6 x3y6)(adjacent x3y6 x2y6)(adjacent x2y6 x2y7)(adjacent x2y7 x2y6)(is_floor x3y6)(adjacent x3y6 x4y6)(adjacent x4y6 x3y6)(adjacent x3y6 x3y7)(adjacent x3y7 x3y6)(is_floor x4y6)(adjacent x4y6 x5y6)(adjacent x5y6 x4y6)(adjacent x4y6 x4y7)(adjacent x4y7 x4y6)(is_floor x5y6)(adjacent x5y6 x6y6)(adjacent x6y6 x5y6)(adjacent x5y6 x5y7)(adjacent x5y7 x5y6)(is_floor x6y6)(adjacent x6y6 x7y6)(adjacent x7y6 x6y6)(adjacent x6y6 x6y7)(adjacent x6y7 x6y6)(adjacent x7y6 x7y7)(adjacent x7y7 x7y6)(adjacent x0y7 x1y7)(adjacent x1y7 x0y7)(adjacent x0y7 x0y8)(adjacent x0y8 x0y7)(is_floor x1y7)(adjacent x1y7 x2y7)(adjacent x2y7 x1y7)(adjacent x1y7 x1y8)(adjacent x1y8 x1y7)(is_floor x2y7)(adjacent x2y7 x3y7)(adjacent x3y7 x2y7)(adjacent x2y7 x2y8)(adjacent x2y8 x2y7)(is_floor x3y7)(adjacent x3y7 x4y7)(adjacent x4y7 x3y7)(adjacent x3y7 x3y8)(adjacent x3y8 x3y7)(is_floor x4y7)(adjacent x4y7 x5y7)(adjacent x5y7 x4y7)(adjacent x4y7 x4y8)(adjacent x4y8 x4y7)(adjacent x5y7 x6y7)(adjacent x6y7 x5y7)(adjacent x5y7 x5y8)(adjacent x5y8 x5y7)(is_floor x6y7)(adjacent x6y7 x7y7)(adjacent x7y7 x6y7)(adjacent x6y7 x6y8)(adjacent x6y8 x6y7)(adjacent x7y7 x7y8)(adjacent x7y8 x7y7)(adjacent x0y8 x1y8)(adjacent x1y8 x0y8)(adjacent x0y8 x0y9)(adjacent x0y9 x0y8)(is_floor x1y8)(adjacent x1y8 x2y8)(adjacent x2y8 x1y8)(adjacent x1y8 x1y9)(adjacent x1y9 x1y8)(is_floor x2y8)(adjacent x2y8 x3y8)(adjacent x3y8 x2y8)(adjacent x2y8 x2y9)(adjacent x2y9 x2y8)(is_floor x3y8)(adjacent x3y8 x4y8)(adjacent x4y8 x3y8)(adjacent x3y8 x3y9)(adjacent x3y9 x3y8)(is_floor x4y8)(adjacent x4y8 x5y8)(adjacent x5y8 x4y8)(adjacent x4y8 x4y9)(adjacent x4y9 x4y8)(is_floor x5y8)(adjacent x5y8 x6y8)(adjacent x6y8 x5y8)(adjacent x5y8 x5y9)(adjacent x5y9 x5y8)(is_floor x6y8)(adjacent x6y8 x7y8)(adjacent x7y8 x6y8)(adjacent x6y8 x6y9)(adjacent x6y9 x6y8)(adjacent x7y8 x7y9)(adjacent x7y9 x7y8)(adjacent x0y9 x1y9)(adjacent x1y9 x0y9)(adjacent x1y9 x2y9)(adjacent x2y9 x1y9)(adjacent x2y9 x3y9)(adjacent x3y9 x2y9)(adjacent x3y9 x4y9)(adjacent x4y9 x3y9)(adjacent x4y9 x5y9)(adjacent x5y9 x4y9)(adjacent x5y9 x6y9)(adjacent x6y9 x5y9)(adjacent x6y9 x7y9)(adjacent x7y9 x6y9)(object_at o0 x2y1)(occupied x2y1)(tomato o0)(not-plate o0)(object_at o1 x5y1)(occupied x5y1)(plate o1)(object_at o2 x3y2)(occupied x3y2)(tomato o2)(not-plate o2)(object_at o3 x6y2)(occupied x6y2)(plate o3)(object_at o4 x2y4)(occupied x2y4)(lettuce o4)(not-plate o4)(object_at o5 x3y5)(occupied x3y5)(lettuce o5)(not-plate o5)(object_at o6 x5y7)(occupied x5y7)(plate o6))
(:goal
   (and 
       (delivered o0)
       (tomato o0)
   )
)
)
