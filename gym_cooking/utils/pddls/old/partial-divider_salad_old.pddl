; PDDL file for partial-divider_salad
(define (problem partial-divider_salad)
(:domain grid_overcooked)
(:objects
    x0y0 - cell
    x0y1 - cell
    x0y2 - cell
    x0y3 - cell
    x0y4 - cell
    x0y5 - cell
    x0y6 - cell
    x1y0 - cell
    x1y1 - cell
    x1y2 - cell
    x1y3 - cell
    x1y4 - cell
    x1y5 - cell
    x1y6 - cell
    x2y0 - cell
    x2y1 - cell
    x2y2 - cell
    x2y3 - cell
    x2y4 - cell
    x2y5 - cell
    x2y6 - cell
    x3y0 - cell
    x3y1 - cell
    x3y2 - cell
    x3y3 - cell
    x3y4 - cell
    x3y5 - cell
    x3y6 - cell
    x4y0 - cell
    x4y1 - cell
    x4y2 - cell
    x4y3 - cell
    x4y4 - cell
    x4y5 - cell
    x4y6 - cell
    x5y0 - cell
    x5y1 - cell
    x5y2 - cell
    x5y3 - cell
    x5y4 - cell
    x5y5 - cell
    x5y6 - cell
    x6y0 - cell
    x6y1 - cell
    x6y2 - cell
    x6y3 - cell
    x6y4 - cell
    x6y5 - cell
    x6y6 - cell
    a1 - agent
    a2 - agent
    p1 - object
    p2 - object
    l1 - object
    t1 - object
)

(:init
    (is_cutting_board x0y1)
    (is_cutting_board x0y2)
    (delivery_spot x0y3)
    (is_floor x1y1)
    (is_floor x1y2)
    (is_floor x1y3)
    (is_floor x1y4)
    (is_floor x1y5)
    (is_floor x2y1)
    (is_floor x2y2)
    (is_floor x2y3)
    (is_floor x2y4)
    (is_floor x2y5)
    (is_floor x3y5)
    (is_floor x4y1)
    (is_floor x4y2)
    (is_floor x4y3)
    (is_floor x4y4)
    (is_floor x4y5)
    (object_at t1 x5y0)
    (occupied x5y0)
    (tomato t1)
    (is_floor x5y1)
    (is_floor x5y2)
    (is_floor x5y3)
    (is_floor x5y4)
    (is_floor x5y5)
    (object_at p2 x5y6)
    (occupied x5y6)
    (plate p2)
    (object_at l1 x6y1)
    (occupied x6y1)
    (lettuce l1)
    (object_at p2 x6y5)
    (occupied x6y5)
    (plate p2)
    (agent_at a1 x2y1)
    (holding_nothing a1)
    (agent_at a2 x4y1)
    (holding_nothing a2)
    (adjacent x0y0 x1y0)
    (adjacent x1y0 x0y0)
    (adjacent x0y0 x0y1)
    (adjacent x0y1 x0y0)
    (adjacent x0y1 x1y1)
    (adjacent x1y1 x0y1)
    (adjacent x0y1 x0y2)
    (adjacent x0y2 x0y1)
    (adjacent x0y2 x1y2)
    (adjacent x1y2 x0y2)
    (adjacent x0y2 x0y3)
    (adjacent x0y3 x0y2)
    (adjacent x0y3 x1y3)
    (adjacent x1y3 x0y3)
    (adjacent x0y3 x0y4)
    (adjacent x0y4 x0y3)
    (adjacent x0y4 x1y4)
    (adjacent x1y4 x0y4)
    (adjacent x0y4 x0y5)
    (adjacent x0y5 x0y4)
    (adjacent x0y5 x1y5)
    (adjacent x1y5 x0y5)
    (adjacent x0y5 x0y6)
    (adjacent x0y6 x0y5)
    (adjacent x0y6 x1y6)
    (adjacent x1y6 x0y6)
    (adjacent x1y0 x2y0)
    (adjacent x2y0 x1y0)
    (adjacent x1y0 x1y1)
    (adjacent x1y1 x1y0)
    (adjacent x1y1 x2y1)
    (adjacent x2y1 x1y1)
    (adjacent x1y1 x1y2)
    (adjacent x1y2 x1y1)
    (adjacent x1y2 x2y2)
    (adjacent x2y2 x1y2)
    (adjacent x1y2 x1y3)
    (adjacent x1y3 x1y2)
    (adjacent x1y3 x2y3)
    (adjacent x2y3 x1y3)
    (adjacent x1y3 x1y4)
    (adjacent x1y4 x1y3)
    (adjacent x1y4 x2y4)
    (adjacent x2y4 x1y4)
    (adjacent x1y4 x1y5)
    (adjacent x1y5 x1y4)
    (adjacent x1y5 x2y5)
    (adjacent x2y5 x1y5)
    (adjacent x1y5 x1y6)
    (adjacent x1y6 x1y5)
    (adjacent x1y6 x2y6)
    (adjacent x2y6 x1y6)
    (adjacent x2y0 x3y0)
    (adjacent x3y0 x2y0)
    (adjacent x2y0 x2y1)
    (adjacent x2y1 x2y0)
    (adjacent x2y1 x3y1)
    (adjacent x3y1 x2y1)
    (adjacent x2y1 x2y2)
    (adjacent x2y2 x2y1)
    (adjacent x2y2 x3y2)
    (adjacent x3y2 x2y2)
    (adjacent x2y2 x2y3)
    (adjacent x2y3 x2y2)
    (adjacent x2y3 x3y3)
    (adjacent x3y3 x2y3)
    (adjacent x2y3 x2y4)
    (adjacent x2y4 x2y3)
    (adjacent x2y4 x3y4)
    (adjacent x3y4 x2y4)
    (adjacent x2y4 x2y5)
    (adjacent x2y5 x2y4)
    (adjacent x2y5 x3y5)
    (adjacent x3y5 x2y5)
    (adjacent x2y5 x2y6)
    (adjacent x2y6 x2y5)
    (adjacent x2y6 x3y6)
    (adjacent x3y6 x2y6)
    (adjacent x3y0 x4y0)
    (adjacent x4y0 x3y0)
    (adjacent x3y0 x3y1)
    (adjacent x3y1 x3y0)
    (adjacent x3y1 x4y1)
    (adjacent x4y1 x3y1)
    (adjacent x3y1 x3y2)
    (adjacent x3y2 x3y1)
    (adjacent x3y2 x4y2)
    (adjacent x4y2 x3y2)
    (adjacent x3y2 x3y3)
    (adjacent x3y3 x3y2)
    (adjacent x3y3 x4y3)
    (adjacent x4y3 x3y3)
    (adjacent x3y3 x3y4)
    (adjacent x3y4 x3y3)
    (adjacent x3y4 x4y4)
    (adjacent x4y4 x3y4)
    (adjacent x3y4 x3y5)
    (adjacent x3y5 x3y4)
    (adjacent x3y5 x4y5)
    (adjacent x4y5 x3y5)
    (adjacent x3y5 x3y6)
    (adjacent x3y6 x3y5)
    (adjacent x3y6 x4y6)
    (adjacent x4y6 x3y6)
    (adjacent x4y0 x5y0)
    (adjacent x5y0 x4y0)
    (adjacent x4y0 x4y1)
    (adjacent x4y1 x4y0)
    (adjacent x4y1 x5y1)
    (adjacent x5y1 x4y1)
    (adjacent x4y1 x4y2)
    (adjacent x4y2 x4y1)
    (adjacent x4y2 x5y2)
    (adjacent x5y2 x4y2)
    (adjacent x4y2 x4y3)
    (adjacent x4y3 x4y2)
    (adjacent x4y3 x5y3)
    (adjacent x5y3 x4y3)
    (adjacent x4y3 x4y4)
    (adjacent x4y4 x4y3)
    (adjacent x4y4 x5y4)
    (adjacent x5y4 x4y4)
    (adjacent x4y4 x4y5)
    (adjacent x4y5 x4y4)
    (adjacent x4y5 x5y5)
    (adjacent x5y5 x4y5)
    (adjacent x4y5 x4y6)
    (adjacent x4y6 x4y5)
    (adjacent x4y6 x5y6)
    (adjacent x5y6 x4y6)
    (adjacent x5y0 x6y0)
    (adjacent x6y0 x5y0)
    (adjacent x5y0 x5y1)
    (adjacent x5y1 x5y0)
    (adjacent x5y1 x6y1)
    (adjacent x6y1 x5y1)
    (adjacent x5y1 x5y2)
    (adjacent x5y2 x5y1)
    (adjacent x5y2 x6y2)
    (adjacent x6y2 x5y2)
    (adjacent x5y2 x5y3)
    (adjacent x5y3 x5y2)
    (adjacent x5y3 x6y3)
    (adjacent x6y3 x5y3)
    (adjacent x5y3 x5y4)
    (adjacent x5y4 x5y3)
    (adjacent x5y4 x6y4)
    (adjacent x6y4 x5y4)
    (adjacent x5y4 x5y5)
    (adjacent x5y5 x5y4)
    (adjacent x5y5 x6y5)
    (adjacent x6y5 x5y5)
    (adjacent x5y5 x5y6)
    (adjacent x5y6 x5y5)
    (adjacent x5y6 x6y6)
    (adjacent x6y6 x5y6)
    (adjacent x6y0 x6y1)
    (adjacent x6y1 x6y0)
    (adjacent x6y1 x6y2)
    (adjacent x6y2 x6y1)
    (adjacent x6y2 x6y3)
    (adjacent x6y3 x6y2)
    (adjacent x6y3 x6y4)
    (adjacent x6y4 x6y3)
    (adjacent x6y4 x6y5)
    (adjacent x6y5 x6y4)
    (adjacent x6y5 x6y6)
    (adjacent x6y6 x6y5)
)

(:goal
   (or
        (and (delivered t1)
             (tomato t1)
             (plate t1)
             (chopped t1)
             (lettuce t1))
        (and (delivered p1)
             (tomato p1)
             (plate p1)
             (chopped p1)
             (lettuce p1))
        (and (delivered p2)
             (tomato p2)
             (plate p2)
             (chopped p2)
             (lettuce p2))
        (and (delivered l1)
             (lettuce l1)
             (lettuce l1)
             (plate l1)
             (chopped l1))
   )
)
)
