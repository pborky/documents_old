#lang scheme

(define (even? x) (cond
                    ((= x 1) false)
                    ((= x 0) true)
                    ((< x 0) (even? (+ x 2)))
                    (else (even? (- x 2)))))

(define (rev l) (letrec ((rev2 (lambda (j k) (cond
                                          ((null? j) k)
                                          (else (rev2 (cdr j) (cons (car j) k)))))))
                 (rev2 l '())))
;(rev (list 1 2 3 4 5 6 7))

(define (dup l) (letrec ((in (lambda (a l) 
                               (cond
                                 ((null? l) false)
                                 ((= (car l) a) true)
                                 (else (in a (cdr l)))))) 
                         (dup2 (lambda (l k) 
                                 (cond
                                   ((null? l) l)
                                   ((in (car l) k) (dup2 (cdr l) k))
                                   (else (cons (car l) (dup2 (cdr l) (cons (car l) k)))))))) 
                  (dup2 l '())))
;(dup (list 1 2 3 3 4 5 6 4 7))

(define (flatten l) (letrec ((flat (lambda (j k) 
                                         (cond
                                           ((null? j) k)
                                           ((list? (car j)) (flat (car j) (flat (cdr j) k)))
                                           (else (cons (car j) (flat (cdr j) k)))))))
                      (flat l '())))
;(flatten '(1 (2 3 (3 4)) 5 6 7))

(define (filter p l) (cond
                       ((null? l) '())
                       ((p (car l)) (cons (car l) (filter p (cdr l))))
                       (else (filter p (cdr l)))))
;(filter (lambda (x) (and (< x 5) (>= x 2))) (flatten '(1 (2 3 (3 4)) 5 6 7)))
;(filter even? (flatten '(1 (2 3 (3 4)) 5 6 7)))

(define (at x l) (cond ((= x 0) (car l)) (else (at (- x 1) (cdr l)))))
;(at 4 (flatten '(1 (2 3 (3 4)) 5 6 7)))

(define (at2 x y l) (at x (at y l)))
;(at2 2 0 '((1 2 3 4) (5 6 7 8) (9 10 11 12) (13 14 15 16)))

(define (applyat fn x l) (cond
                          ((= x 0) (cons (fn (car l)) (cdr l)))
                          (else (cons (car l) (applyat fn (- x 1) (cdr l))))))
;(applyat (lambda (x) (- x 4)) 4 (flatten '(1 (2 3 (3 4)) 5 6 7)))

(define (applyat2 fn x y l) (applyat (lambda (k) (applyat fn x k)) y l))
(applyat2 (lambda (x) (+ x 1)) 2 0 '((1 2 3 4) (5 6 7 8) (9 10 11 12) (13 14 15 16)))

(define (incat i l) (applyat (lambda (x) (+ x 1)) i l))
;(incat 4 (flatten '(1 (2 3 (3 4)) 5 6 7)))

(define (subsat y i l) (applyat (lambda (x) y) i l))
;(subsat 10 4 (flatten '(1 (2 3 (3 4)) 5 6 7)))

(define (incat2 x y l) (applyat2 (lambda (x) (+ x 1)) x y l))
;(incat2 2 0 '((1 2 3 4) (5 6 7 8) (9 10 11 12) (13 14 15 16)))
