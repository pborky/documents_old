
(define (problem big-problem5)
    (:domain signs)
    (:objects
        buff - buffer
        place1 place2 - workplace
        trigon circle square - shape
        blue yellow red green - color
        board0 board1 board2 board3 board4 board5 - board
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
        (at board5 buff)
    )
    (:goal
        (and
            (at board0 buff)
            (at board1 buff)
            (at board2 buff)
            (at board3 buff)
            (at board4 buff)
            (at board5 buff)

            (has-color board0 red)
            (has-color board1 blue)
            (has-color board2 red)
            (has-color board3 red)
            (has-color board4 red)
            (has-color board5 red)

            (has-shape board0 trigon)
            (has-shape board1 circle)
            (has-shape board2 square)
            (has-shape board3 square)
            (has-shape board4 square)
            (has-shape board5 trigon)
        )
    )
    (:metric minimize (total-cost))
)

