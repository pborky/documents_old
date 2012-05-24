(define (domain signs)
    
    (:requirements :typing :action-costs)

    (:types buffer workplace board shape color)

    (:predicates
        (expert-mode)
        (advanced-mode)

        (in-hand-board ?board - board )
        (in-hand-saw)
        (in-hand-paint)
        (hand-free)
	    
        (at ?x - board ?y - buffer)
        (mounted ?x - board ?y - workplace)
        (empty ?x - workplace)
        
        (cuted ?x - board )
        (has-shape ?x - board ?y - shape)

        (painted ?x - board )
        (has-color ?x - board ?y - color)
    )

    (:functions
        (total-cost)
    )

    (:action pick
        :parameters ( ?board - board ?place - buffer)
        :precondition (and (hand-free) (at ?board ?place))
        :effect (and
            (in-hand-board ?board)
            (not (hand-free))
            (not (at ?board ?place)) ) )

    (:action grasp-saw
        :parameters ()
        :precondition (and (hand-free))
        :effect (and
            (in-hand-saw)
            (not (hand-free))
            (increase (total-cost) 1) ) )

    (:action grasp-paint
        :parameters ()
        :precondition (and (hand-free))
        :effect (and
            (in-hand-paint)
            (not (hand-free))
            (increase (total-cost) 1) ) )

    (:action stash
        :parameters ( ?board - board ?place - buffer)
        :precondition (and (in-hand-board ?board))
        :effect (and
            (not (in-hand-board ?board))
            (hand-free)
            (at ?board ?place) ) )

     (:action do-saw
        :parameters ( ?board - board ?place - workplace ?shape - shape)
        :precondition (and
            (in-hand-saw)
            (mounted ?board ?place)
            (not (cuted ?board)))
        :effect (and
            (cuted ?board)
            (has-shape ?board ?shape)
            (increase (total-cost) 8)) )

     (:action do-paint
        :parameters ( ?board - board ?place - workplace ?color - color)
        :precondition (and
            (in-hand-paint)
            (mounted ?board ?place)
            (cuted ?board)
            (not (painted ?board)))
        :effect (and
            (painted ?board)
            (has-color ?board ?color)
            (increase (total-cost) 12)) )


    (:action drop-saw
        :parameters ()
        :precondition (and (in-hand-saw))
        :effect (and
            (not (in-hand-saw))
            (hand-free)
            (increase (total-cost) 1) ) )

    (:action drop-paint
        :parameters ()
        :precondition (and (in-hand-paint))
        :effect (and
            (not (in-hand-paint))
            (hand-free)
            (increase (total-cost) 1) ) )

    (:action mount
        :parameters ( ?board - board ?place - workplace)
        :precondition (and (in-hand-board ?board) (empty ?place) )
        :effect (and
            (not (in-hand-board ?board))
            (hand-free)
            (mounted ?board ?place)
            (not (empty ?place))
            (increase (total-cost) 4) ) )

    (:action umount
        :parameters ( ?board - board ?place - workplace)
        :precondition (and (hand-free) (mounted ?board ?place) )
        :effect (and
            (in-hand-board ?board)
            (not (hand-free))
            (not (mounted ?board ?place))
            (empty ?place)
            (increase (total-cost) 4) ) )

    (:action switch-advanced
        :parameters ()
        :precondition (and (not (advanced-mode)) (not (expert-mode)))
        :effect (and
            (advanced-mode)
            (increase (total-cost) 15)
        )
    )

    (:action switch-expert
        :parameters ()
        :precondition (and (advanced-mode) (not (expert-mode)))
        :effect (and
            (not (advanced-mode))
            (expert-mode)
            (increase (total-cost) 22)
        )
    )

)




