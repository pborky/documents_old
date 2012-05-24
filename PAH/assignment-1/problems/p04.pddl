
(define (problem big-problem4)
    (:domain signs)
    (:objects
        buff - buffer
        place1 place2 - workplace
        trigon circle square - shape
        blue yellow red green - color
        board0 board1 board2 board3 board4 - board
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
        (at board4 buff)
    )
    (:goal
        (and
            (at board0 buff)
            (at board1 buff)
            (at board2 buff)
            (at board3 buff)
            (at board4 buff)

            (has-color board0 blue)
            (has-color board1 red)
            (has-color board2 blue)
            (has-color board3 blue)
            (has-color board4 blue)

            (has-shape board0 circle)
            (has-shape board1 trigon)
            (has-shape board2 square)
            (has-shape board3 circle)
            (has-shape board4 circle)
        )
    )
    (:metric minimize (total-cost))
)

