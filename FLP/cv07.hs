filter p xs = [ x | x <- xs, p x ]

--primes = sieve [2..] where sieve (p:xp) = p: sieve [ x | x <- xp, (mod x p) /= 0  ]

data Natural = MakeNat Integer
data TCons a b = Cons a b | Empty

instance Show Natural where 
  show a = "N"++show(fromNatural(a))

instance Eq Natural where
  (a) == (b) = fromNatural(a) == fromNatural(b)

data Bt a = Bnil | Bnode ( Bt a ) a ( Bt a )

elements :: Bt a -> [a]
elements (Bnil) = []
elements (Bnode l y p) = elements(l)++(y:elements(p))

instance (Eq a) => Eq(Bt a) where
  (Bnil) == (Bnil) = True
  (Bnode l x p) == (Bnode ll xx pp) = x == xx && l == ll && p == pp
  (_) == (_) = False

instance (Show a) => Show (Bt a) where
  show (Bnil) = "."
  show (Bnode l x p) = "("++show(l)++","++show(x)++","++show(p)++")"

toNatural :: Integer -> Natural
toNatural x | x > 0  = MakeNat x
	    | otherwise = error "Zaporne!"

fromNatural :: Natural -> Integer
fromNatural (MakeNat x) = x

primes = let sieve = (\ (s) (p:xp) -> p : (s s [ x | x <- xp, (mod x p) /= 0  ]) ) in (sieve sieve [2..] )
