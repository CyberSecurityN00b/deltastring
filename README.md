# deltastring
A String Obfuscation Proof-of-Concept

While working on my [shellfeck](https://github.com/CyberSecurityN00b/shellfeck) project, specifically researching various BrainF\*ck generator algorithms, it became apparent that the good BrainF\*ck generators went with calculating the deltas between characters and providing instructions based on the delta. Taking this concept, I made a proof-of-concept where a delta is calculated based on a given formula, and the string is built that way. For the proof-of-concept, I've thrown in a cybersec aspect by passing the delta to `system`.

Another feature that I've tacked on to this is entropy specification. You can specify certain parameters for the desired entropy (higher entropy, lower entropy, or closest to a target goal entropy), and the deltastring code will try to give you something approaching this. Given how this is implemented, it's a bit brute force, so it may not be exact or you may be limited by the provided formula.

## Usage

 - Run `./generate_deltastring_code.py --cmdline <cmdline> --formula <formula>`
 - Compile the output code with `gcc`
 - Run the compiled executable!

_See the Formulas and Entropy sections further below._

### Examples

  - `./generate_deltastring_code.py --cmdline "netstat -plantu" --formula "c + x * x - x"`
  - `./generate_deltastring_code.py --cmdline "whoami" --formula "c + x - x" --entropy-mode closest --entropy-goal 5.555`

## Formulas

To make the deltastring a bit more dynamic, a formula needs to be provided. This formula is used to calculate the delta, meaning some formulas just won't work and some will give higher or lower entropy than others.

Formulas must include at least one `c` variable and one `x` variable, as well as operations. Numbers are permitted in the formula, as well as the following mathematical operators/symbols: `+-*/()%&|<>~^`. The characters are evaluated in both Python and C, so keep this in mind (i.e., it is legal to use `||` as far as the deltastring parser is concerned, but this won't result in anything useful).

The `c` variable represents the value of the previous character as an integer. For the first iteration, it is the value of 0.

The `x` variable represents a placeholder, and can be used multiple times with each instance being a separate variable. For example, the formula `c + x + x + x` becomes `c + x[0] + x[1] + x[2]`. More variables means a bigger delta string, and may increase the amount of time to generate the deltastring due to the randomized bruteforce method of generate the values of x.

Some formulas to get started:
  - `c * x + x` - _The original formula that helped to inspire the project._
  - `c + x - x` - _Results in deltastrings with an entropy between 3.0 and 4.0 during testings._
  - `x + 13 - c` - _Demonstrates hardcoded numbers are part of a formula._
  - `(c | 13) + (x[0] & 42) - x[1]` - _Demonstrates bitwise operators, as well as the need for parenthesis in this case._
  - `(c * 0) + x + x` - _Not really a delta string, as ignores the previous characters, but useful if you want to bypass the delta concept and still generate an obfuscated string._

## Entropy

Entropy calculations can play a part in attempting to determine aspects about data, such as whether it is likely to be English or whether it is likely to be encrypted. While the formula that is specified ultimately dictates the possibly entropy values of the deltastring, this project allows for you to specify a preference with the following arguments:

  - `--entropy-mode` - Specifies the entropy mode, with a default of `none`. The following modes are supported:
     - `none` - _Only generates one deltastring and gives you that._
     - `highest` - _Generates multiple deltastrings and returns the one with the highest shannon entropy._
     - `lowest` - _Generates multiple deltastrings and returns the one with the lowest shannon entropy._
     - `closest` - _Generates multiple deltastrings and returns the one closest to your desired shannon entropy, specified by `--entropy-goal`._
   - `--entropy-goal` - Specifies the shannon entropy goal as a floating point value. Only relevant with `--entropy-mode closest`. Default value is `4.0`.
   - `--entropy-iterations` - Specifies how many deltastrings should be generated before returning the one that best matches the desired entropy. Default value is `100`.

## Bruteforce Failsafe

Since deltastring makes a randomized bruteforce attempt at finding the values that work with the formula to give the desired delta, a failsafe is in place so it doesn't get stuck in an infinite loop when a formula is provided which can't give the desired value. This is accomplished with the `--max-iterations` parameter, which has a default value of `256*256`.
