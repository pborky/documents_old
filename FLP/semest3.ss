;#lang racket
;(require racket/trace)
  
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
                      ((not expr) (set-failed state 'unknown-procedure-call))
                      ; procedure recursion limit exceeded
                      ((< lim 0) (set-failed state 'recursion-limit-exceeded))
                      ; recursion limit exceeded
                      ((< steps 0) (set-failed state 'recursion-limit-exceeded))
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
                       (do (do state (get-procedure (car expr) prg) prg (- lim 1) steps) (cdr expr) prg lim (- steps 1)))
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


(define 
  (merge-sort l)
  
  (define (merge pred l k)
    (cond
      ((null? l) k)
      ((null? k) l)
      ((null? pred) (cons (car l) (cons (car k) (merge (cdr l) (cdr k)))))
      (else (let ((al (car l))
                  (ak (car k)))
              (cond
                ((pred al ak) (cons al (merge pred (cdr l) k)))
                (else (cons ak (merge pred l (cdr k)))) ))) ))
  (define
    (split l)
    (define 
      (spl l i)
      (cond
        ((null? l) (cons (ceiling (/ i 2)) l))
        (else (let ((ret (spl (cdr l) (+ i 1))))
                (let ((ar (car ret))
                      (dr (cdr ret)))
                  (cond
                    ((list? ar) (cons (cons (car l) ar) dr))
                    ((<= ar i) (cons ar (cons (car l) dr)) )
                    (else (cons (cons (car l) '()) dr) ) ) )) )))
    (spl l 0))
  
  (define
    (pivotal pred l k)
    (cond
      ((null? l) #f)
      ((= (car l) (car k)) (pivotal pred (cdr l) (cdr k)))
      ((pred (car l) (car k)) #t)
      (else #f) ))
  
  (define (pred a b) (pivotal < (car a) (car b)))
  (cond
    ((null? l) l)
    ((null? (cdr l)) l)
    (else (let ((k (split l)))
            (merge pred
                   (merge-sort (car k))
                   (merge-sort (cdr k)))) ) ))

(define (evaluate prgs pairs threshold stack-size)
  (letrec
      ((manhatan-dst (lambda (l k) 
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
        (lambda (prg pairs threshold stack-size prglen maxsteps)
          (cond
            ((null? pairs) '(0 0 0 0))
            (else
             (let
                 ( (value (proc-pair prg (cdr pairs) threshold stack-size prglen maxsteps)) )
               (cond
                 ((all? <= value threshold) (map + value (ex prg (car pairs) threshold stack-size prglen (- maxsteps (apply (lambda (a b c d) d) value)))))
                 (else value) )  ) ) ) ))
       (proc-prg 
        (lambda (prgs pairs threshold stack-size)
          (cond
            ((null? prgs) prgs)
            (else 
             (let
                 ((prglen (lengthf (lambda (a) (cond ((eq? a 'procedure) #f) ((eq? a 'if) #f) (else #t) )) (car prgs)))
                  (maxprglen (apply (lambda (a b c d) c) threshold))
                  (maxsteps (apply (lambda (a b c d) d) threshold)))
               (cond
                 ((> prglen maxprglen) (proc-prg (cdr prgs) pairs threshold stack-size))
                 (else
                  (let
                      ((value (apply (lambda (a b c d) (list a b prglen d)) (proc-pair (car prgs) pairs threshold stack-size prglen maxsteps) )))
                    (cond
                      ((all? <= value threshold) (cons (list value (car prgs)) (proc-prg (cdr prgs) pairs threshold stack-size)) )
                      (else (proc-prg (cdr prgs) pairs threshold stack-size)) ) ) )))  )) )) )
    (merge-sort  (proc-prg prgs pairs threshold stack-size)) ))

(define (congruential-rng seed)
  (let ((a 16807 #|(expt 7 5)|#)
        (m 2147483647 #|(- (expt 2 31) 1)|#))
    (let ((m-1 (- m 1)))
      (let ((seed (+ (remainder seed m-1) 1)))
        (lambda (b)
          (let ((n (remainder (* a seed) m)))
            (set! seed n)
            (quotient (* (- n 1) b) m-1)))))))


(define
  (circular l)
  (define
    (circ l k)
    (cond
      ((null? l) #f)
      ((null? (cdr l)) (set-cdr! l k) k)
      (#t (circ (cdr l) k)) ) )
  ;(display l)(newline)
  (circ l l))

(define 
  (evolve pairs threshold stack-size)
  
  (define (lengthf skip? skip skipcnt l)
    (cond
      ((null? l) 0)
      ((list? (car l)) (+ (lengthf skip? skip skipcnt (car l)) (lengthf skip? skip skipcnt (cdr l))))
      ((skip? (car l)) (+ skipcnt (lengthf skip? skip skipcnt (skip l '()))))
      (#t (+ 1 (lengthf skip? skip skipcnt (cdr l)))) ) )
  
  (define
    (skip? a)
    (eq? a 'if))
  (define 
    (skip l k)
    (cond 
      ((null? k) (cdr (cdr l)))
      (#t (cons (car l) (cons (car (cdr l)) k )) ) ))  
  (define
    (choose-at skip? skip skipcnt l n)
    (cond
      ((null? l) (list n l '()))
      ((skip? (car l)) (choose-at skip? skip skipcnt (skip l '()) n))
      ((<= n 0) (list -1 (car l) '()))
      ((list? (car l))
       (apply
        (lambda 
            (nn ll rr)
          (cond
            ((< nn 0) (list nn ll rr))
            (#t (choose-at skip? skip skipcnt (cdr l) nn)) ) )
        (choose-at skip? skip skipcnt (car l) (- n 1)) ))
      (#t (choose-at skip? skip skipcnt (cdr l) (- n 1))) ))  
  (define
    (replace-at-m skip? skip skipcnt l mix n)
    (cond
      ((null? l) (list n l '()))
      ((skip? (car l))
       (apply 
        (lambda (nn ll rest) (list nn (skip l ll) rest))
        (replace-at-m skip? skip skipcnt (skip l '()) mix n) ) )
      ((<= n 0) (list -1 (cons (mix (car l)) (cdr l)) (car l)) )
      ((list? (car l))
       (apply
        (lambda 
            (nn ll rest)
          (cond 
            ((< nn 0) (list nn (cons ll (cdr l)) rest))
            (#t 
             (apply
              (lambda 
                  (nnn lll rest) 
                (list nnn (cons ll lll) rest))
              (replace-at-m skip? skip skipcnt (cdr l) mix nn)) ) )) 
        (replace-at-m skip? skip skipcnt (car l) mix (- n 1)) ) )
      (#t 
       (apply
        (lambda 
            (nn ll rest)
          (list nn (cons (car l) ll) rest))
        (replace-at-m skip? skip skipcnt (cdr l) mix (- n 1))) )) )
  
  (define
    (replace-at skip? skip skipcnt l k n)
    (define
      (pack-result n x l k)
      (cond
        ((null? x) (list n l k))
        (#t (list n (cons x l) k) ) ))
    (cond
      ((null? l) (list n l '()))
      ((skip? (car l))
       (apply 
        (lambda (nn ll rest) (list nn (skip l ll) rest))
        (replace-at skip? skip skipcnt (skip l '()) k n) ) )
      ((<= n 0) (list -1 (cons k (cdr l)) (car l)) )
      ((list? (car l))
       (apply
        (lambda 
            (nn ll rest)
          (cond 
            ((< nn 0) (list nn (cons ll (cdr l)) rest))
            (#t 
             (apply
              (lambda 
                  (nnn lll rest) 
                (list nnn (cons ll lll) rest))
              (replace-at skip? skip skipcnt (cdr l) k nn)) ) )) 
        (replace-at skip? skip skipcnt (car l) k (- n 1)) ) )
      (#t 
       (apply
        (lambda 
            (nn ll rest)
          (list nn (cons (car l) ll) rest))
        (replace-at skip? skip skipcnt (cdr l) k (- n 1))) )) )

    
  (define n-genes 6)
  (define n-predicates 3)
  (define predicates (circular '(mark? wall? west?)))
  (define genes
    (circular
     (append 
      '(turn-left put-mark get-mark step start)
      (list (lambda (fnc rng) (list 'if (fnc predicates #f (rng n-predicates) rng) (fnc genes #f (rng n-genes) rng) (fnc genes 'if (rng n-genes) rng) ))
            (lambda (fnc rng) (list (fnc genes #f (rng n-genes) rng) (fnc genes #f (rng n-genes) rng) )) ) )))
  
  (define
    (mix a rng)
    (define 
      (get-at l a i rng)
      (let ((a  (cond
                  ((null? l) l)
                  ((<= i 0) (cond
                              ((eq? a (car l)) (get-at (cdr l) a (- i 1) rng))
                              (#t (car l)) ) )
                  (#t (get-at (cdr l) a (- i 1) rng))  )))
        (cond
          ((procedure? a) (a get-at rng)) (#t a) )) )
    ;(trace get-at)
    (get-at genes a (rng n-genes) rng))
  
  (define
    (mutate entity len rng)
    
    (apply
     (lambda (n l r) l)
     (replace-at-m skip? skip 2 entity (lambda (a) (mix a rng)) (rng len)) ))
  
  (define ; take 2 trees and generate 2 other where random subtrees are excanged at single point
    (crossover mother father lm lf rng)
    (let 
        ((im (rng lm))
         (if (rng lf)))
      (apply
       (lambda (n xm ym)
         (apply
          (lambda (n l r)
            (list l (apply (lambda (n ll r) ll) (replace-at skip? skip 2 mother r im)) ) )
          (replace-at skip? skip 2 father xm if) ) )
       (choose-at skip? skip 2 mother im)) ) )
  
  
  (define ; http://en.wikipedia.org/wiki/Stochastic_universal_sampling
    (stochstic-universal-sampling population max-individuals fitness-fnc rng)
    
    (define
      (roulette-wheel l u ptr roulette-step)
      ;(display (list "bounds=<" (* 1. l) "," (* 1. u) ">," "step=" ptr ))(newline)
      (cond
        ((> ptr u) #f)
        ((and (> ptr l) (<= ptr u)) #t)
        (#t (roulette-wheel l u (+ ptr roulette-step) roulette-step)) ))
    
    (define (sus population roulette-step sub-total-fitness idx max min rand)      
      (cond
        ((null? population) (list (fitness-fnc idx min max sub-total-fitness) min max '()))
        (#t (apply 
             (lambda
                 (a b c d)
               (let 
                   ((fitness (+ 1 a b)))
                 (letrec
                     ((mx (cond ((null? max) fitness) ((> fitness max) fitness) (#t max)  ))
                      (mi (cond ((null? min) fitness) ((< fitness min) fitness) (#t min)  )))
                   (apply
                    (lambda (total-fitness min max rest)
                      (let
                          ((lower (/ (fitness-fnc idx min max sub-total-fitness) total-fitness))
                           (upper (/ (fitness-fnc (+ 1 idx) min max (+ sub-total-fitness fitness)) total-fitness)))
                        (cond
                          ((roulette-wheel lower upper rand roulette-step)  (list total-fitness min max (cons (car population) rest) ))
                          (#t (list total-fitness min max rest)) ) ))
                    (sus (cdr population) roulette-step (+ sub-total-fitness fitness) (+ idx 1) mx mi rand) ) )) )
             (car (car population)) ))  ) )
    
    ;(trace sus)
    ;(trace roulette-wheel)
    (cond 
      ((= 0 max-individuals) '())
      (#t
       (car (cdr (cdr (cdr (sus population (/ 1. max-individuals) 0 0 '() '() (/ (rng 1000000.) (* max-individuals 1000000.))) ))) ))))
     
  (define ; from given population select 'max-individuals individuals. 
    ; 'elite of them are copied and others are selected by stochastic universal sapling
    (select population max-individuals elite rng)
    
    (cond
      ((null? population) '())
      ((<= max-individuals 0) '())
      ((<= elite 0)
       (stochstic-universal-sampling 
        population 
        max-individuals 
        (lambda (idx min max cum-fitness) (- (* idx (+ min max)) cum-fitness))
        rng ))
      (#t
       (display (car population))(newline)
       (cons (car population) (select (cdr population) (- max-individuals 1) (- elite 1) rng) )) ) )
  
  (define
    (generate population max-mutants max-offsprings rng)
    ;(trace lengthf)
    (define
      (make-offspring population rng)
      (cond
        ((null? population) '())
        ((null? (cdr population)) '())
        (#t (let ((parA (car population))
                  (parB (car (cdr population))))
              (let ((prgA (car (cdr parA)) )
                    (prgB (car (cdr parB)) ))
                (let ((startA (car (cdr (cdr (car prgA )))))
                      (startB (car (cdr (cdr (car prgB )))))
                      (restA (cdr prgA) ))
                  (let ((lenA (lengthf skip? skip 2 startA))
                        (lenB (lengthf skip? skip 2 startB)))
                    (apply
                     (lambda
                         (offsA offsB)
                       (cons (cons (list 'procedure 'start offsA) restA)
                             (cons (cons (list 'procedure 'start offsB) restA)
                                   (make-offspring (cdr (cdr population)) rng) ) ) )
                     (crossover startA startB lenA lenB rng) ))))   ) ) ) )
    (append
     (map
      (lambda (individual)
        (apply
         (lambda
             (value prg)
           (let ((start (car (cdr (cdr (car prg)))))
                 (rest (cdr prg)) )
             (cons (list 'procedure 'start (mutate start (lengthf skip? skip 2 start) rng) ) rest) ))
         individual ))
      (stochstic-universal-sampling
       population 
       max-mutants
       (lambda (idx min max cum-fitness) cum-fitness)
       rng) )
     (make-offspring
      (stochstic-universal-sampling
       population 
       max-offsprings 
       (lambda (idx min max cum-fitness) (- (* idx (+ min max)) cum-fitness))
       rng) rng)  ) )
  
  (define max-individuals 50)
  (define max-elite 2)
  (define max-new-mutatns 30)
  (define max-new-offspring 30)
  (define
    (do offspring ancestors pairs threshold stack-size rng)
    (letrec
        ((population (select (merge-sort (append ancestors (evaluate offspring pairs threshold stack-size))) max-individuals max-elite rng)))
      (do (generate population max-new-mutatns max-new-offspring rng) population pairs threshold stack-size rng)))
  
  (define init-prgs 
    '( 
      ( (procedure start ((if west? (turn-left put-mark) (if wall? (turn-left) (put-mark))) (if mark? (step) ()) start) ) )
      ( (procedure start (put-mark step)) )
      ( (procedure start ((if wall? (turn-left) (put-mark)) (if mark? (step) ()) start) ) )
      ( (procedure start (turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start ) ) 
        (procedure turn-right (turn-left turn-left turn-left turn-left turn-left)) ) 
      ( (procedure start (put-mark (if wall? turn-left step) start)) ) 
      ( (procedure start (step step step put-mark)) )
      ( (procedure start (turn-left put-mark step step )) )
      ( (procedure start (step step step put-mark)) )
      ( (procedure start (step start)) )
      ( (procedure start ((if wall? () (2)) put-mark)) (procedure 2 (step start () step)))
      ( (procedure start ((if west? () (turn-left)) start)) )
      ( (procedure start (() turn-left turn-left turn-left)) )
      ( (procedure start (put-mark 1 put-mark)) (procedure 1 (turn-left turn-left turn-left step)) )
      ( (procedure start ((if wall? () (2)) put-mark)) (procedure 2 (step start () step)))
      ( (procedure start ((if wall? (turn-left) (put-mark step)) start )) )
      ( (procedure start (turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start)) (procedure turn-right (turn-left turn-left turn-left turn-left turn- left)))) )
  
  (define hermafrodit '(turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start ))
  ;(define rng (let ((t (current-seconds))) (congruential-rng (* (truncate (/ t 10000)) (* 1000000 (modulo t 10000)) ))))
  (define rng (congruential-rng 344544334564))
  (display (list pairs threshold stack-size))(newline)
  (let
      ((len (lengthf skip? skip 2 hermafrodit)))
    (do init-prgs '() pairs threshold stack-size rng)
    ;(show-c (crossover hermafrodit hermafrodit len len rng))
    ;(show-m (mutate hermafrodit len rng))
    )
  )


















;(evolve '() '() 0)
(define s0
'((
(w w w)
 (w 1 w)
(w w w)
)
(1 1) east
))

(define t0
'((
(w w w)
 (w 0 w)
(w w w)
)
(1 1) northwest
))

(define s1
'((
(w w w)
 (w 0 w)
(w 0 w)
 (w w w)
)
(1 1) northeast
))

(define t1
'((
(w w w)
 (w 1 w)
(w 1 w)
 (w w w)
)
(1 2) northeast
))

(define s2
'((
(w w w w w w w w w)
 (w 0 0 0 0 0 0 0 w)
(w w w w w w w w w)
)
(1 1) west
))

(define t2
'((
(w w w w w w w w w)
 (w 1 1 1 1 1 1 1 w)
(w w w w w w w w w)
)
(7 1) east
))

(define s3
'((
(w w w w w w w w w)
 (w 0 0 0 0 0 0 0 w)
(w 0 0 0 0 0 0 0 w)
 (w w w w w w w w w)
)
(1 1) west
))

(define t3
'((
(w w w w w w w w w)
 (w 1 1 1 1 1 1 1 w)
(w 1 1 1 1 1 1 1 w)
 (w w w w w w w w w)
)
(1 2) west
))

(define pairs '( ( (((w w w w w w) (w 0 w 0 w w) (w 1 w 0 0 w) (w 1 0 0 w w) (w w w w w w)) (1 3) southwest) (((w w w w w w) (w 0 w 0 w w) (w 0 w 0 0 w) (w 0 0 0 w w) (w w w w w w)) (1 1) northeast) ) ( (((w w w w w w) (w 0 w 0 w w) (w 0 w 2 0 w) (w 1 3 0 w w) (w w w w w w)) (3 3) northwest) (((w w w w w w) (w 0 w 0 w w) (w 0 w 0 0 w) (w 0 0 0 w w) (w w w w w w)) (1 1) northeast) )) )

; '(turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start )
;(define prgs '( ( (procedure start (turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start ) ) (procedure turn-right (turn-left turn-left turn-left turn-left turn-left)) ) ( (procedure start (put-mark (if wall? turn-left step) start)) ) ( (procedure start (step step step put-mark)) ) ) ) (define pairs '( ( (((w w w w w w) (w 0 w 0 w w) (w 1 w 0 0 w) (w 1 0 0 w w) (w w w w w w)) (1 3) southwest) (((w w w w w w) (w 0 w 0 w w) (w 0 w 0 0 w) (w 0 0 0 w w) (w w w w w w)) (1 1) northeast) ) ( (((w w w w w w) (w 0 w 0 w w) (w 0 w 2 0 w) (w 1 3 0 w w) (w w w w w w)) (3 3) northwest) (((w w w w w w) (w 0 w 0 w w) (w 0 w 0 0 w) (w 0 0 0 w w) (w w w w w w)) (1 1) northeast) )) )
;(evolve pairs '(20 20 20 20) 5)

;(trace evaluate)
;(evolve `((,s0 ,t0) (,s1 ,t1) (,s2 ,t2) (,s3 ,t3)  ) `(10000 10000 300 1000) 30)
(evolve `((,s0 ,t0)   ) `(10000 10000 300 1000) 30)
;(evolve pairs `(10000 10000 20 20) 10)
;(define prgs '( ( (procedure start (turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start ) ) (procedure turn-right (turn-left turn-left turn-left turn-left turn-left)) ) ( (procedure start (put-mark (if wall? turn-left step) start)) ) ( (procedure start (step step step put-mark)) ) ) ) (define pairs '( ( (((w w w w w w) (w 0 w 0 w w) (w 1 w 0 0 w) (w 1 0 0 w w) (w w w w w w)) (1 3) southwest) (((w w w w w w) (w 0 w 0 w w) (w 0 w 0 0 w) (w 0 0 0 w w) (w w w w w w)) (1 1) northeast) ) ( (((w w w w w w) (w 0 w 0 w w) (w 0 w 2 0 w) (w 1 3 0 w w) (w w w w w w)) (3 3) northwest) (((w w w w w w) (w 0 w 0 w w) (w 0 w 0 0 w) (w 0 0 0 w w) (w w w w w w)) (1 1) northeast) )) )
  (define init-prgs 
    '( 
      ( (procedure start ((if wall? (turn-left) (put-mark)) (if mark? (step) ()) start) ) )
      ( (procedure start (turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start ) ) 
        (procedure turn-right (turn-left turn-left turn-left turn-left turn-left)) ) 
      ( (procedure start (put-mark (if wall? turn-left step) start)) ) 
      ( (procedure start (step step step put-mark)) )
      ( (procedure start (turn-right (if wall? (turn-left (if wall? (turn-left (if wall? turn-left step)) step)) step) put-mark start)) (procedure turn-right (turn-left turn-left turn-left turn-left turn-left)))) )
  
;(evaluate '(( (procedure start (step step step start)) )) `((,s0 ,t0)) `(10000 10000 100 1000) 10)
;(simulate s0 'start '( (procedure start (step step step start)) ) 100)