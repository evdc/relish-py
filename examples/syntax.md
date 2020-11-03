Syntax for working with sets / relations

## Verbose syntax

Basic: `for n : Neighbors(...) where n.state == Hidden do Detonate(n)`
Anonymous: `for Neighbors where .state == Hidden do Detonate(.)`

## Operator syntax

`Neighbors[state == Hidden] -> { Detonate(_) }`

## Relations: "Subscript" syntax

`relation Board[c: Cell, d: Digit]`
`n_this_digit(digit) = count(Board[*, digit])`
`for c : Cell do Board[c] := Blank`
`for c : Cell do set Board[c, Blank]`
`for c : Cell do Board <- (c, Blank)`
`possible_positions += this_position`   set insert
`possible_positions <- this_position`
`set possible_positions[this_position]`
`possible_positions[this_position].`    as in datalog

## Relations: "Function" syntax

`rel Board(Cell) => Digit`
`n_this_digit(digit) = count(c: Cell where Board(c) == digit)`
`n_this_digit(digit) = count(Board(_) == digit)`
`for c : Cell do Board(c) := Blank`
`let Board(c) := Blank forall c: Cell`
`let possible_positions(this_position)`

Function syntax is a little more "natural" to devs used to functions, but harder to express 1) reverse lookup and 2) updates.
Also, the "subscript" syntax does correspond more naturally to the operational semantics.

There are some exceptions: consider
`drinker_ids = age[_, . >= 21]` vs. `drinker_ids = p: Person where age(p) >= 21`

There's always syntax sugar: e.g. `Board[c, _]` can be rewritten as `Board[c]` for familiarity.
Or the above query as `Person where .age >= 21` assuming the `.age` is expanded to `Person__age` by combining with the LHS of the `where` operator.
