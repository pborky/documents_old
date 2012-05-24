
(define (problem big-problem1)
    (:domain signs)
    (:objects
        buff - buffer
        place1 place2 - workplace
        trigon circle square - shape
        blue yellow red green - color
        board0 board1 - board
    )
    (:init
        (empty place1)
        (empty place2)
        (hand-free)
        (= (total-cost) 0)

        (at board0 buff)
        (at board1 buff)
    )
    (:goal
        (and
            (at board0 buff)
            (at board1 buff)

            (has-color board0 yellow)
            (has-color board1 yellow)

            (has-shape board0 trigon)
            (has-shape board1 circle)
        )
    )
    (:metric minimize (total-cost))
)

