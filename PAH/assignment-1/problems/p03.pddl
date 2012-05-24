
(define (problem big-problem3)
    (:domain signs)
    (:objects
        buff - buffer
        place1 place2 - workplace
        trigon circle square - shape
        blue yellow red green - color
        board0 board1 board2 board3 - board
    )
    (:init
        (empty place1)
        (empty place2)
        (hand-free)
        (= (total-cost) 0)

        (at board0 buff)
        (at board1 buff)
        (at board2 buff)
        (at board3 buff)
    )
    (:goal
        (and
            (at board0 buff)
            (at board1 buff)
            (at board2 buff)
            (at board3 buff)

            (has-color board0 yellow)
            (has-color board1 green)
            (has-color board2 red)
            (has-color board3 yellow)

            (has-shape board0 circle)
            (has-shape board1 circle)
            (has-shape board2 circle)
            (has-shape board3 circle)
        )
    )
    (:metric minimize (total-cost))
)

