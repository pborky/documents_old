#lang scheme


(define
  (from n)
  (cons n (delay (from (+ n 1))) ))

(define
  (range n m)
  (cond 
    ((= n m) '())
    (#t (cons n (delay (range (+ n 1) m)) )) ) )

(define
  (rest l)
  (let ((e (cdr l)))
    (cond
      ((list? e) e)
      (#t (force e)) ) ))

(define
  (take n stream)
  (cond
    ((null? stream) stream)
    ((null? n) (cons (car stream) (take n (rest stream))))
    ((= n 0) '())
    (#t (cons (car stream) (take (- n 1) (rest stream))))
    ))

;(rest (from 9))
;(take 10 (from 9))
;(take 20 (range 0 10))

(define
  (append l k)
  (cond
    ((null? l) k)
    (#t (cons (car l) (delay (append (rest l) k)) )) ))

;(take 30 (append (take 10 (from 9)) (from 100)))

(define
  (lazy-map fn l)
  (cond
    ((null? l) '())
    (#t (cons (fn (car l)) (delay (lazy-map fn (rest l))) )) ))

(lazy-map (lambda (x) (+ x 1)) '(1 2 3 4 5 6 7) )


(define
  (power-set set)
  (cond
    ((null? set) (cons set '()))
    (#t 
     (let ((sets (power-set (cdr set)))) 
       (append sets (lazy-map (lambda (s) (cons (car set) s)) sets) ) ))
   ))

(power-set '(1 2 43))

(define
  (remove e l)
  (cond
    ((= e (car l)) (cdr l)) 
    (#t (cons (car l) (delay (remove e (rest l)))) )))

(take '() (remove 2 '( 1 2 3 4 )))

(define 
  (permute set)
  (cond
    ((null? set) (cons set '()))
    ((null? (rest set)) (cons set '())) 
    (#t
     (apply 
      append
      (map
       (lambda
           (element)
         (lazy-map (lambda (y) (cons element y)) (permute (remove element set))) )
       set)))
    ))

(permute '(1 2 3))
