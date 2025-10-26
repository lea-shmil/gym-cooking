; PDDL file for large_tomato_3
(define (problem large_tomato_3)
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
    x1y0 - cell
    x1y1 - cell
    x1y2 - cell
    x1y3 - cell
    x1y4 - cell
    x1y5 - cell
    x1y6 - cell
    x1y7 - cell
    x1y8 - cell
    x2y0 - cell
    x2y1 - cell
    x2y2 - cell
    x2y3 - cell
    x2y4 - cell
    x2y5 - cell
    x2y6 - cell
    x2y7 - cell
    x2y8 - cell
    x3y0 - cell
    x3y1 - cell
    x3y2 - cell
    x3y3 - cell
    x3y4 - cell
    x3y5 - cell
    x3y6 - cell
    x3y7 - cell
    x3y8 - cell
    x4y0 - cell
    x4y1 - cell
    x4y2 - cell
    x4y3 - cell
    x4y4 - cell
    x4y5 - cell
    x4y6 - cell
    x4y7 - cell
    x4y8 - cell
    x5y0 - cell
    x5y1 - cell
    x5y2 - cell
    x5y3 - cell
    x5y4 - cell
    x5y5 - cell
    x5y6 - cell
    x5y7 - cell
    x5y8 - cell
    x6y0 - cell
    x6y1 - cell
    x6y2 - cell
    x6y3 - cell
    x6y4 - cell
    x6y5 - cell
    x6y6 - cell
    x6y7 - cell
    x6y8 - cell
    x7y0 - cell
    x7y1 - cell
    x7y2 - cell
    x7y3 - cell
    x7y4 - cell
    x7y5 - cell
    x7y6 - cell
    x7y7 - cell
    x7y8 - cell
    x8y0 - cell
    x8y1 - cell
    x8y2 - cell
    x8y3 - cell
    x8y4 - cell
    x8y5 - cell
    x8y6 - cell
    x8y7 - cell
    x8y8 - cell
    x9y0 - cell
    x9y1 - cell
    x9y2 - cell
    x9y3 - cell
    x9y4 - cell
    x9y5 - cell
    x9y6 - cell
    x9y7 - cell
    x9y8 - cell
    a1 - agent
    a2 - agent
    a3 - agent
    o0 - veggieOrPlate
    o1 - veggieOrPlate
    o2 - veggieOrPlate
)

(:init
    (agent_at a1 x2y1)
    (holding_nothing a1)
    (occupied x2y1)
    (agent_at a2 x7y1)
    (holding_nothing a2)
    (occupied x7y1)
    (agent_at a3 x7y7)
    (holding_nothing a3)
    (occupied x7y7)
    (adjacent x0y0 x1y0)
    (adjacent x1y0 x0y0)
    (adjacent x0y0 x0y1)
    (adjacent x0y1 x0y0)
    (adjacent x1y0 x2y0)
    (adjacent x2y0 x1y0)
    (adjacent x1y0 x1y1)
    (adjacent x1y1 x1y0)
    (adjacent x2y0 x3y0)
    (adjacent x3y0 x2y0)
    (adjacent x2y0 x2y1)
    (adjacent x2y1 x2y0)
    (adjacent x3y0 x4y0)
    (adjacent x4y0 x3y0)
    (adjacent x3y0 x3y1)
    (adjacent x3y1 x3y0)
    (adjacent x4y0 x5y0)
    (adjacent x5y0 x4y0)
    (adjacent x4y0 x4y1)
    (adjacent x4y1 x4y0)
    (adjacent x5y0 x6y0)
    (adjacent x6y0 x5y0)
    (adjacent x5y0 x5y1)
    (adjacent x5y1 x5y0)
    (adjacent x6y0 x7y0)
    (adjacent x7y0 x6y0)
    (adjacent x6y0 x6y1)
    (adjacent x6y1 x6y0)
    (adjacent x7y0 x8y0)
    (adjacent x8y0 x7y0)
    (adjacent x7y0 x7y1)
    (adjacent x7y1 x7y0)
    (adjacent x8y0 x9y0)
    (adjacent x9y0 x8y0)
    (adjacent x8y0 x8y1)
    (adjacent x8y1 x8y0)
    (adjacent x9y0 x9y1)
    (adjacent x9y1 x9y0)
    (is_cutting_board x0y1)
    (adjacent x0y1 x1y1)
    (adjacent x1y1 x0y1)
    (adjacent x0y1 x0y2)
    (adjacent x0y2 x0y1)
    (is_floor x1y1)
    (adjacent x1y1 x2y1)
    (adjacent x2y1 x1y1)
    (adjacent x1y1 x1y2)
    (adjacent x1y2 x1y1)
    (is_floor x2y1)
    (adjacent x2y1 x3y1)
    (adjacent x3y1 x2y1)
    (adjacent x2y1 x2y2)
    (adjacent x2y2 x2y1)
    (is_floor x3y1)
    (adjacent x3y1 x4y1)
    (adjacent x4y1 x3y1)
    (adjacent x3y1 x3y2)
    (adjacent x3y2 x3y1)
    (is_floor x4y1)
    (adjacent x4y1 x5y1)
    (adjacent x5y1 x4y1)
    (adjacent x4y1 x4y2)
    (adjacent x4y2 x4y1)
    (adjacent x5y1 x6y1)
    (adjacent x6y1 x5y1)
    (adjacent x5y1 x5y2)
    (adjacent x5y2 x5y1)
    (adjacent x6y1 x7y1)
    (adjacent x7y1 x6y1)
    (adjacent x6y1 x6y2)
    (adjacent x6y2 x6y1)
    (is_floor x7y1)
    (adjacent x7y1 x8y1)
    (adjacent x8y1 x7y1)
    (adjacent x7y1 x7y2)
    (adjacent x7y2 x7y1)
    (is_floor x8y1)
    (adjacent x8y1 x9y1)
    (adjacent x9y1 x8y1)
    (adjacent x8y1 x8y2)
    (adjacent x8y2 x8y1)
    (adjacent x9y1 x9y2)
    (adjacent x9y2 x9y1)
    (adjacent x0y2 x1y2)
    (adjacent x1y2 x0y2)
    (adjacent x0y2 x0y3)
    (adjacent x0y3 x0y2)
    (is_floor x1y2)
    (adjacent x1y2 x2y2)
    (adjacent x2y2 x1y2)
    (adjacent x1y2 x1y3)
    (adjacent x1y3 x1y2)
    (is_floor x2y2)
    (adjacent x2y2 x3y2)
    (adjacent x3y2 x2y2)
    (adjacent x2y2 x2y3)
    (adjacent x2y3 x2y2)
    (is_floor x3y2)
    (adjacent x3y2 x4y2)
    (adjacent x4y2 x3y2)
    (adjacent x3y2 x3y3)
    (adjacent x3y3 x3y2)
    (is_floor x4y2)
    (adjacent x4y2 x5y2)
    (adjacent x5y2 x4y2)
    (adjacent x4y2 x4y3)
    (adjacent x4y3 x4y2)
    (adjacent x5y2 x6y2)
    (adjacent x6y2 x5y2)
    (adjacent x5y2 x5y3)
    (adjacent x5y3 x5y2)
    (adjacent x6y2 x7y2)
    (adjacent x7y2 x6y2)
    (adjacent x6y2 x6y3)
    (adjacent x6y3 x6y2)
    (is_floor x7y2)
    (adjacent x7y2 x8y2)
    (adjacent x8y2 x7y2)
    (adjacent x7y2 x7y3)
    (adjacent x7y3 x7y2)
    (is_floor x8y2)
    (adjacent x8y2 x9y2)
    (adjacent x9y2 x8y2)
    (adjacent x8y2 x8y3)
    (adjacent x8y3 x8y2)
    (adjacent x9y2 x9y3)
    (adjacent x9y3 x9y2)
    (delivery_spot x0y3)
    (adjacent x0y3 x1y3)
    (adjacent x1y3 x0y3)
    (adjacent x0y3 x0y4)
    (adjacent x0y4 x0y3)
    (is_floor x1y3)
    (adjacent x1y3 x2y3)
    (adjacent x2y3 x1y3)
    (adjacent x1y3 x1y4)
    (adjacent x1y4 x1y3)
    (is_floor x2y3)
    (adjacent x2y3 x3y3)
    (adjacent x3y3 x2y3)
    (adjacent x2y3 x2y4)
    (adjacent x2y4 x2y3)
    (adjacent x3y3 x4y3)
    (adjacent x4y3 x3y3)
    (adjacent x3y3 x3y4)
    (adjacent x3y4 x3y3)
    (is_floor x4y3)
    (adjacent x4y3 x5y3)
    (adjacent x5y3 x4y3)
    (adjacent x4y3 x4y4)
    (adjacent x4y4 x4y3)
    (is_floor x5y3)
    (adjacent x5y3 x6y3)
    (adjacent x6y3 x5y3)
    (adjacent x5y3 x5y4)
    (adjacent x5y4 x5y3)
    (is_floor x6y3)
    (adjacent x6y3 x7y3)
    (adjacent x7y3 x6y3)
    (adjacent x6y3 x6y4)
    (adjacent x6y4 x6y3)
    (is_floor x7y3)
    (adjacent x7y3 x8y3)
    (adjacent x8y3 x7y3)
    (adjacent x7y3 x7y4)
    (adjacent x7y4 x7y3)
    (is_floor x8y3)
    (adjacent x8y3 x9y3)
    (adjacent x9y3 x8y3)
    (adjacent x8y3 x8y4)
    (adjacent x8y4 x8y3)
    (adjacent x9y3 x9y4)
    (adjacent x9y4 x9y3)
    (adjacent x0y4 x1y4)
    (adjacent x1y4 x0y4)
    (adjacent x0y4 x0y5)
    (adjacent x0y5 x0y4)
    (is_floor x1y4)
    (adjacent x1y4 x2y4)
    (adjacent x2y4 x1y4)
    (adjacent x1y4 x1y5)
    (adjacent x1y5 x1y4)
    (is_floor x2y4)
    (adjacent x2y4 x3y4)
    (adjacent x3y4 x2y4)
    (adjacent x2y4 x2y5)
    (adjacent x2y5 x2y4)
    (is_cutting_board x3y4)
    (adjacent x3y4 x4y4)
    (adjacent x4y4 x3y4)
    (adjacent x3y4 x3y5)
    (adjacent x3y5 x3y4)
    (is_floor x4y4)
    (adjacent x4y4 x5y4)
    (adjacent x5y4 x4y4)
    (adjacent x4y4 x4y5)
    (adjacent x4y5 x4y4)
    (is_floor x5y4)
    (adjacent x5y4 x6y4)
    (adjacent x6y4 x5y4)
    (adjacent x5y4 x5y5)
    (adjacent x5y5 x5y4)
    (is_floor x6y4)
    (adjacent x6y4 x7y4)
    (adjacent x7y4 x6y4)
    (adjacent x6y4 x6y5)
    (adjacent x6y5 x6y4)
    (is_floor x7y4)
    (adjacent x7y4 x8y4)
    (adjacent x8y4 x7y4)
    (adjacent x7y4 x7y5)
    (adjacent x7y5 x7y4)
    (is_floor x8y4)
    (adjacent x8y4 x9y4)
    (adjacent x9y4 x8y4)
    (adjacent x8y4 x8y5)
    (adjacent x8y5 x8y4)
    (adjacent x9y4 x9y5)
    (adjacent x9y5 x9y4)
    (adjacent x0y5 x1y5)
    (adjacent x1y5 x0y5)
    (adjacent x0y5 x0y6)
    (adjacent x0y6 x0y5)
    (is_floor x1y5)
    (adjacent x1y5 x2y5)
    (adjacent x2y5 x1y5)
    (adjacent x1y5 x1y6)
    (adjacent x1y6 x1y5)
    (is_floor x2y5)
    (adjacent x2y5 x3y5)
    (adjacent x3y5 x2y5)
    (adjacent x2y5 x2y6)
    (adjacent x2y6 x2y5)
    (adjacent x3y5 x4y5)
    (adjacent x4y5 x3y5)
    (adjacent x3y5 x3y6)
    (adjacent x3y6 x3y5)
    (is_floor x4y5)
    (adjacent x4y5 x5y5)
    (adjacent x5y5 x4y5)
    (adjacent x4y5 x4y6)
    (adjacent x4y6 x4y5)
    (is_floor x5y5)
    (adjacent x5y5 x6y5)
    (adjacent x6y5 x5y5)
    (adjacent x5y5 x5y6)
    (adjacent x5y6 x5y5)
    (is_floor x6y5)
    (adjacent x6y5 x7y5)
    (adjacent x7y5 x6y5)
    (adjacent x6y5 x6y6)
    (adjacent x6y6 x6y5)
    (is_floor x7y5)
    (adjacent x7y5 x8y5)
    (adjacent x8y5 x7y5)
    (adjacent x7y5 x7y6)
    (adjacent x7y6 x7y5)
    (is_floor x8y5)
    (adjacent x8y5 x9y5)
    (adjacent x9y5 x8y5)
    (adjacent x8y5 x8y6)
    (adjacent x8y6 x8y5)
    (adjacent x9y5 x9y6)
    (adjacent x9y6 x9y5)
    (adjacent x0y6 x1y6)
    (adjacent x1y6 x0y6)
    (adjacent x0y6 x0y7)
    (adjacent x0y7 x0y6)
    (is_floor x1y6)
    (adjacent x1y6 x2y6)
    (adjacent x2y6 x1y6)
    (adjacent x1y6 x1y7)
    (adjacent x1y7 x1y6)
    (is_floor x2y6)
    (adjacent x2y6 x3y6)
    (adjacent x3y6 x2y6)
    (adjacent x2y6 x2y7)
    (adjacent x2y7 x2y6)
    (is_floor x3y6)
    (adjacent x3y6 x4y6)
    (adjacent x4y6 x3y6)
    (adjacent x3y6 x3y7)
    (adjacent x3y7 x3y6)
    (is_floor x4y6)
    (adjacent x4y6 x5y6)
    (adjacent x5y6 x4y6)
    (adjacent x4y6 x4y7)
    (adjacent x4y7 x4y6)
    (is_floor x5y6)
    (adjacent x5y6 x6y6)
    (adjacent x6y6 x5y6)
    (adjacent x5y6 x5y7)
    (adjacent x5y7 x5y6)
    (is_floor x6y6)
    (adjacent x6y6 x7y6)
    (adjacent x7y6 x6y6)
    (adjacent x6y6 x6y7)
    (adjacent x6y7 x6y6)
    (is_floor x7y6)
    (adjacent x7y6 x8y6)
    (adjacent x8y6 x7y6)
    (adjacent x7y6 x7y7)
    (adjacent x7y7 x7y6)
    (is_floor x8y6)
    (adjacent x8y6 x9y6)
    (adjacent x9y6 x8y6)
    (adjacent x8y6 x8y7)
    (adjacent x8y7 x8y6)
    (adjacent x9y6 x9y7)
    (adjacent x9y7 x9y6)
    (adjacent x0y7 x1y7)
    (adjacent x1y7 x0y7)
    (adjacent x0y7 x0y8)
    (adjacent x0y8 x0y7)
    (is_floor x1y7)
    (adjacent x1y7 x2y7)
    (adjacent x2y7 x1y7)
    (adjacent x1y7 x1y8)
    (adjacent x1y8 x1y7)
    (is_floor x2y7)
    (adjacent x2y7 x3y7)
    (adjacent x3y7 x2y7)
    (adjacent x2y7 x2y8)
    (adjacent x2y8 x2y7)
    (is_floor x3y7)
    (adjacent x3y7 x4y7)
    (adjacent x4y7 x3y7)
    (adjacent x3y7 x3y8)
    (adjacent x3y8 x3y7)
    (is_floor x4y7)
    (adjacent x4y7 x5y7)
    (adjacent x5y7 x4y7)
    (adjacent x4y7 x4y8)
    (adjacent x4y8 x4y7)
    (is_floor x5y7)
    (adjacent x5y7 x6y7)
    (adjacent x6y7 x5y7)
    (adjacent x5y7 x5y8)
    (adjacent x5y8 x5y7)
    (is_floor x6y7)
    (adjacent x6y7 x7y7)
    (adjacent x7y7 x6y7)
    (adjacent x6y7 x6y8)
    (adjacent x6y8 x6y7)
    (is_floor x7y7)
    (adjacent x7y7 x8y7)
    (adjacent x8y7 x7y7)
    (adjacent x7y7 x7y8)
    (adjacent x7y8 x7y7)
    (is_floor x8y7)
    (adjacent x8y7 x9y7)
    (adjacent x9y7 x8y7)
    (adjacent x8y7 x8y8)
    (adjacent x8y8 x8y7)
    (adjacent x9y7 x9y8)
    (adjacent x9y8 x9y7)
    (adjacent x0y8 x1y8)
    (adjacent x1y8 x0y8)
    (adjacent x1y8 x2y8)
    (adjacent x2y8 x1y8)
    (adjacent x2y8 x3y8)
    (adjacent x3y8 x2y8)
    (adjacent x3y8 x4y8)
    (adjacent x4y8 x3y8)
    (adjacent x4y8 x5y8)
    (adjacent x5y8 x4y8)
    (adjacent x5y8 x6y8)
    (adjacent x6y8 x5y8)
    (adjacent x6y8 x7y8)
    (adjacent x7y8 x6y8)
    (adjacent x7y8 x8y8)
    (adjacent x8y8 x7y8)
    (adjacent x8y8 x9y8)
    (adjacent x9y8 x8y8)
    (object_at o0 x9y1)
    (occupied x9y1)
    (tomato o0)
    (not-plate o0)
    (object_at o1 x9y5)
    (occupied x9y5)
    (plate o1)
    (object_at o2 x6y8)
    (occupied x6y8)
    (plate o2)
)

(:goal
   (and 
       (delivered o0)
       (tomato o0)
   )
)
)
