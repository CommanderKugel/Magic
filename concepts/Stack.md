## The Stack

1. Beginning of step of phase
2. Do State Based Actions
3. Triggered Abilities (Beginning of Phase/Step) go on the stack.

4. Player whose turn it is receives Priority

5. Player with Priority
- cast one spell
- activate one ability
- pass

6. Player with priority passed?
No  -> Go to No. 5.
Yes -> Go to No. 6.

7. Have all players passed without anyone doing smt?
No  ->
- Do State Based Actions. 
- Next Player receives Priority.
- Go to No. 5.
Yes -> Go to No. 8.

8. Is the Stack empty?
No  -> Resolve the top element of the Stack. Go to No. 3.
Yes -> End of step or phase.
