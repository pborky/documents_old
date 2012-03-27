
(define (simulate-preempt state expr prg lim steps)
        (letrec 
             (; data              
              (orientations (list 'west 'southwest 'southeast 'east 'northeast 'northwest 'west))
              
              ; general functions
              (even? ; true if argument x is even
               (lambda (x) 
                 (cond
                    ((= x 1) #f)
                    ((= x 0) #t)
                    ((< x 0) (even? (+ x 2)))
                    (else (even? (- x 2))) )))
              (reverse ; return reversed list l
               (lambda (l) 
                 (letrec 
                     ((rev
                       (lambda (j k) 
                         (cond
                           ((null? j) k)
                           (else (rev (cdr j) (cons (car j) k))) ))))
                   (rev l '()) )))
              (at ; i-th element of the list l
               (lambda (i l)
                 (cond
                   ((< i 0) '())
                   ((null? l) '())
                   ((= i 0) (car l))
                   (else (at (- i 1) (cdr l))) ) ))
              (apply-at ; apply fn on i-th element of the list l
               (lambda (fn i l)
                 (cond
                   ((= i 0) (cons (fn (car l)) (cdr l)))
                   ((null? l) (cons '() (apply-at fn (- i 1) (cdr l))))
                   (else (cons (car l) (apply-at fn (- i 1) (cdr l)))) )))
              (at-xy ; x-th element of y-th sublist of list l
               (lambda (x y l) (at x (at y l))))
              (apply-at-xy ; apply fn on x-th element of y-th sublist of list l
               (lambda (fn x y l) (apply-at (lambda (k) (apply-at fn x k)) y l)))
              (inc-at ; increment i-th element of the list l
               (lambda (i l) (apply-at (lambda (a) (+ a 1)) i l)))
              (dec-at ; decrement i-th element of the list l
               (lambda (i l) (apply-at (lambda (a) (- a 1)) i l)))
              (inc-at-xy ; increment x-th element of y-th sublist of list l
               (lambda (l x y) (apply-at-xy (lambda (a) (+ a 1)) x y l)))
              (dec-at-xy ; decrement x-th element of y-th sublist of list l
               (lambda (l x y) (apply-at-xy (lambda (a) (- a 1)) x y l)))
              (trunc-list ; keep first i elements of the list l
               (lambda (i l)
                 (cond 
                   ((null? l) l)
                   ((= i 0) '())
                   (else (cons (car l) (trunc-list (- i 1) (cdr l)))) )))
              
              ; simulator functions
              (apply-state ; generic
               (lambda (fnc state)
                 (apply (lambda (steps maze pos orient) (apply (lambda (x y) (fnc steps maze x y orient)) pos)) state ) ))
              (apply-state2 ; generic
               (lambda (fnc state) (apply fnc state)) )
              (init-state ;
               (lambda (state) (cons (seq-elem '() '()) state) ))
              (get-maze  ; get actual maze
               (lambda (state)
                 (apply-state2 (lambda (steps maze pos orient) maze) state) ))
              (get-coords  ; coordinates of robot
               (lambda (state)
                 (apply-state2 (lambda (steps maze pos orient) pos) state) ))
              (get-coord-x  ; x-coordinate of robot
               (lambda (state)
                 (apply-state (lambda (steps maze x y orient) x) state) ) )
              (get-coord-y  ; y-coordinate of robot
               (lambda (state)
                 (apply-state (lambda (steps maze x y orient) y) state) ) )
              (get-orientation ; get robot`s orientation
               (lambda (state)
                 (apply-state2 (lambda (steps maze pos orient) orient) state) ) )
              (set-orientation ; set robot`s orientation
               (lambda (state o)
                 (apply-state2 (lambda (steps maze pos orient) (list steps maze pos o)) state) ))
              (seq-elem
               (lambda (steps a)
                 (lambda (y)
                       (cond
                         ((null? a) y)
                         ((not (null? steps)) (steps (cons a y))) ))))
              (push-sequence ; put something to action-sequence list
               (lambda (state a)
                 (apply-state2 
                  (lambda (steps maze pos orient)
                    (list (seq-elem steps a) maze pos orient)) state) ))
              ;(lambda (state a) (apply-at (lambda (o) (cons (list a (get-orientation state) (get-coords state)) o)) 0 state )))
              (inc-coord-x ; increment x-coordinate of robot
               (lambda (state)
                 (apply 
                  (lambda (steps maze pos orient)
                    (list steps maze (apply (lambda (x y) (list (+ 1 x) y)) pos) orient)) state ) ))
              (inc-coord-y ; increment y-coordinate of robot
               (lambda (state)
                 (apply 
                  (lambda (steps maze pos orient)
                    (list steps maze (apply (lambda (x y) (list x (+ 1 y))) pos) orient)) state ) ))
              (dec-coord-x ; decrement x-coordinate of robot
               (lambda (state)
                 (apply 
                  (lambda (steps maze pos orient)
                    (list steps maze (apply (lambda (x y) (list (- 1 x) y)) pos) orient)) state ) ))
              (dec-coord-y ; decrement y-coordinate of robot
               (lambda (state)
                 (apply 
                  (lambda (steps maze pos orient)
                    (list steps maze (apply (lambda (x y) (list x (- 1 y))) pos) orient)) state ) ))
              ;(get-failed ; return if execution subtree failed
              ; (lambda (state)
              ;   (apply 
              ;    (lambda (steps maze pos orient)
              ;      (cond ((null? steps) #f) ((null? (car steps)) #t)) ) state )) )
              ;(set-failed ; execution subtree failed
              ; (lambda (state) (push-sequence state '()) ))
              (get-failed ; return if execution subtree failed
               (lambda (state)
                 (not (null? (at 4 state))) ))
              (set-failed ; execution subtree failed
               (lambda (state reason)
                 (append state (list #t)) ))
                 ;(push-sequence (append state (list true)) reason) ))
              (next-orientation ; rotate left helper function
               (lambda (o l)
                 (cond
                   ((null? l) 'fail) ; this should not happen
                   ((eq? (car l) o) (car (cdr l)))
                   (else (next-orientation o (cdr l))) ) ))
              (put-mark ; put mark 
               (lambda (state)
                 (apply-state2 (lambda (steps maze pos orient) (list steps (apply inc-at-xy (cons maze pos )) pos orient)) state) ))
              (get-mark ; get mark 
               (lambda (state)
                 (apply-state2 (lambda (steps maze pos orient) (list steps (apply dec-at-xy (cons maze pos )) pos orient)) state) ))
              (turn-left ; rotate left 
               (lambda (state)
                 (apply-state2 (lambda (steps maze pos orient) (list steps maze pos (next-orientation orient orientations))) state) ))
              (step ; make step without check
               (lambda (state)
                 (apply-state
                  (lambda (steps maze x y orient)
                    (cond
                      ((eq? orient 'west) (list steps maze (list (- x 1) y) orient))
                      ((eq? orient 'east) (list steps maze (list (+ x 1) y) orient))
                      ((even? y) (cond
                                   ((eq? orient 'northwest) (list steps maze (list (- x 1) (- y 1)) orient))
                                   ((eq? orient 'southwest) (list steps maze (list (- x 1) (+ y 1)) orient))
                                   ((eq? orient 'northeast) (list steps maze (list x (- y 1)) orient))
                                   ((eq? orient 'southeast) (list steps maze (list x (+ y 1)) orient)) ))
                      (else (cond
                              ((eq? orient 'northwest) (list steps maze (list x (- y 1)) orient))
                              ((eq? orient 'southwest) (list steps maze (list x (+ y 1)) orient))
                              ((eq? orient 'northeast) (list steps maze (list (+ x 1) (- y 1)) orient))
                              ((eq? orient 'southeast) (list steps maze (list (+ x 1) (+ y 1)) orient)) ))) )
                 state)) )
              (west? ; true if looking to the west
               (lambda (state)
                 (apply-state2 (lambda (steps maze pos orient) (eq? orient 'west)) state) ))
              (mark? ; tru if there is an mark
               (lambda (state)
                 (apply-state (lambda (steps maze x y orient) (> (at-xy x y maze) 0) ) state) ))
              (wall? ; true if there is a wall
               (lambda (state)
                 (apply-state (lambda (steps maze x y orient) (eq? (at-xy x y maze) 'w) ) state) ))
              (get-predicate ; return proper predicate
               (lambda (expr)
                 (cond 
                   ((eq? (at 1 expr) 'wall?) (lambda (state) (wall? (step state))))
                   ((eq? (at 1 expr) 'west?) west?)
                   ((eq? (at 1 expr) 'mark?) mark?)
                   (else '()) ) ))
              (get-if ; return branch body based on predicate
               (lambda (state expr)
                 (cond
                   (((get-predicate expr) state) (cons (at 2 expr) '()))
                   (else (cons (at 3 expr) '()) ) ) ))
              (get-procedure ; return procedure body
               (lambda (expr prg)
                 (cond
                   ((null? prg) #f)
                   ((and (eq? (at 0 (car prg)) 'procedure) (eq? (at 1 (car prg)) expr)) (cons (at 2 (car prg)) '()) )
                   (else (get-procedure expr (cdr prg))) )) )
              
              (do ; entry point
                  (lambda (state expr prg lim steps)
                    (cond 
                      ; nothing to do
                      ((null? expr)  state)
                      ; unknown procedure has been called
                      ((not expr)  (set-failed state 'unknown-procedure-call))
                      ; procedure recursion limit exceeded
                      ((< lim 0) (set-failed state 'recursion-limit-exceeded))
                      ; recursion limit exceeded
                      ((< steps -1) (set-failed state 'recursion-limit-exceeded))
                      ; if execution subtree failed
                      ((get-failed state) state)
                      ; another list? we need to go deeper
                      ((list? (car expr))
                       (do (do state (car expr) prg lim steps) (cdr expr) prg lim steps))
                      ; if 
                      ((eq? (car expr) 'if)
                       (do state (get-if state expr) prg lim steps))
                      ; turn left
                      ((eq? (car expr) 'turn-left)
                       (do (turn-left (push-sequence state 'turn-left)) (cdr expr) prg lim (- steps 1)))
                      ; put mark
                      ((eq? (car expr) 'put-mark)
                       (do (put-mark (push-sequence state 'put-mark)) (cdr expr) prg lim (- steps 1)))
                      ; get mark
                      ((eq? (car expr) 'get-mark)
                       (cond 
                         ((mark? state) (do (get-mark (push-sequence state 'get-mark)) (cdr expr) prg lim (- steps 1)) )
                          (else (set-failed state 'try-to-get-mark-on-empty-field)) ) )
                      ; step
                      ((eq? (car expr) 'step)
                       (let 
                           ((nextstate (step state)))
                         (cond 
                           ((wall? nextstate) (set-failed state 'stepped-to-wall))
                           (else (do (push-sequence nextstate 'step ) (cdr expr) prg lim (- steps 1))) )))
                      ; handle procedure calls
                      (else 
                       (do (do state (get-procedure (car expr) prg) prg (- lim 1) steps) (cdr expr) prg lim steps))
                      ; that`s all
                      )) )  )
          ; exec entry point
          (let ((ret ; bind the return state with "ret" - we need to mangle it a bit
                 (do (init-state state) (cond ((list? expr) expr) (else (list expr))) prg lim steps)))
          (list 
           ((car ret) '()) ; reverse the action list
           (trunc-list 3 (cdr ret)) ; discard any obsolete items
           )) ))

(define (simulate state expr prg lim)
  (simulate-preempt state expr prg lim 999999999))

(define (evaluate prgs pairs threshold stack-size)
  (letrec
      (
       (manhatan-dst (lambda (l k) 
                       (apply +
                              (map
                               (lambda (x y)
                                 (cond
                                   ((list? x) (manhatan-dst x y))
                                   ((eq? x y) 0)
                                   ((< x y) (- y x))
                                   (else (- x y)) ))
                               l k ) )))
       (filter (lambda (pred l)
                 (cond 
                   ((null? l) '())
                   ((pred (car l)) (cons (car l) (filter pred (cdr l))))
                   (else (filter pred (cdr l))) )))
       (length (lambda (l) 
                 (cond
                   ((null? l) 0)
                   (else (+ 1 (length (cdr l)))) )))
       (lengthf (lambda (pred l)
                 (cond
                   ((null? l) 0)
                   ((list? (car l)) (+ (lengthf pred (car l)) (lengthf pred (cdr l))))
                   ((pred (car l)) (+ 1 (lengthf pred (cdr l))))
                   (else (lengthf pred (cdr l))) )))
       (all? (lambda (pred l k)
               (cond
                 ((null? l) #t)
                 ((pred (car l) (car k)) (all? pred (cdr l) (cdr k)))
                 (else #f) ) ))
       (merge (lambda (pred l k)
                (cond
                  ((null? l) k)
                  ((null? k) l)
                  ((null? pred) (cons (car l) (cons (car k) (merge (cdr l) (cdr k)))))
                  (else (let ((al (car l))
                              (ak (car k)))
                          (cond
                            ((pred al ak) (cons al (merge pred (cdr l) k)))
                            (else (cons ak (merge pred l (cdr k)))) ))) )))
       (spl (lambda (l i)
              (cond
                ((null? l) (cons (ceiling (/ i 2)) l))
                (else (let ((ret (spl (cdr l) (+ i 1))))
                        (let ((ar (car ret))
                              (dr (cdr ret)))
                          (cond
                            ((list? ar) (cons (cons (car l) ar) dr))
                            ((<= ar i) (cons ar (cons (car l) dr)) )
                            (else (cons (cons (car l) '()) dr) ) ) )) ))))
       (split (lambda (l) (spl l 0)))
       (merge-sort (lambda (pred l)
                     (cond
                       ((null? l) l)
                       ((null? (cdr l)) l)
                       (#t (let ((k (split l)))
                             (merge pred
                                    (merge-sort pred (car k))
                                    (merge-sort pred (cdr k)))) ) )))
       (pivotal (lambda (pred l  k)
                  (cond
                    ((null? l) #f)
                    ((= (car l) (car k)) (pivotal pred (cdr l) (cdr k)))
                    ((pred (car l) (car k)) #t)
                    (else #f) ) ) )
       (ex
        (lambda (prg pair threshold stack-size prglen maxsteps)
          (apply
           (lambda (init final)
             (apply
              (lambda (expmaze exppos exporient)
                (apply
                 (lambda (steps state)
                   (apply
                    (lambda (maze pos orient)
                      (list
                       (manhatan-dst maze expmaze)
                       (+ (cond ((eq? exporient orient) 0) (else 1)) (manhatan-dst pos exppos))
                       0
                       (length steps) ) )
                    state) )
                 (simulate-preempt init 'start prg stack-size maxsteps) ) )
              final)  )
           pair ) ) )
       (proc-pair
        (lambda (prg pairs threshold stack-size prglen)
          (cond
            ((null? pairs) '(0 0 0 0))
            (else
             (let
                 ((value (proc-pair prg (cdr pairs) threshold stack-size prglen))
                  (maxsteps (apply (lambda (a b c d) d) threshold)))
               (cond
                 ((all? <= value threshold) (map + value (ex prg (car pairs) threshold stack-size prglen maxsteps)) )
                 (else value) ) ) ) ) ))
       (proc-prg 
        (lambda (prgs pairs threshold stack-size)
          (cond
            ((null? prgs) prgs)
            (else 
             (let
                 ((prglen (lengthf (lambda (a) (cond ((eq? a 'procedure) #f) ((eq? a 'if) #f) (else #t) )) (car prgs)))
                  (maxprglen (apply (lambda (a b c d) c) threshold)))
               (cond
                 ((> prglen maxprglen) (proc-prg (cdr prgs) pairs threshold stack-size))
                 (else
                  (let
                    ((value (apply (lambda (a b c d) (list a b prglen d)) (proc-pair (car prgs) pairs threshold stack-size prglen) )))
                    (cond
                      ((all? <= value threshold) (cons (list value (car prgs)) (proc-prg (cdr prgs) pairs threshold stack-size)) )
                      (else (proc-prg (cdr prgs) pairs threshold stack-size)) ) ) )))  )) )) )
    (merge-sort 
     (lambda (a b) (pivotal < (car a) (car b)))
     (proc-prg prgs pairs threshold stack-size)) ))




























(define prgs '( ( (procedure start (turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start ) ) (procedure turn-right (turn-left turn-left turn-left turn-left turn-left)) ) ( (procedure start (put-mark (if wall? turn-left step) start)) ) ( (procedure start (step step step put-mark)) ) ) ) (define pairs '( ( (((w w w w w w) (w 0 w 0 w w) (w 1 w 0 0 w) (w 1 0 0 w w) (w w w w w w)) (1 3) southwest) (((w w w w w w) (w 0 w 0 w w) (w 0 w 0 0 w) (w 0 0 0 w w) (w w w w w w)) (1 1) northeast) ) ( (((w w w w w w) (w 0 w 0 w w) (w 0 w 2 0 w) (w 1 3 0 w w) (w w w w w w)) (3 3) northwest) (((w w w w w w) (w 0 w 0 w w) (w 0 w 0 0 w) (w 0 0 0 w w) (w w w w w w)) (1 1) northeast) )) )
(evaluate prgs pairs '(20 20 20 20) 5)