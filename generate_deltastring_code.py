#!/usr/bin/env python3

import argparse
import collections
import math
import re
import secrets

expanded_formula = ""

def generate_deltastring(string,formula,maxiterations):
    global expanded_formula
    def nums_from_formula(oldchar,newchar,formula,maxiterations):
        x_count = formula.count("x")
        delta = (ord(newchar)-ord(oldchar)) & 255
        iterations = 0
        c = ord(oldchar)
        
        while True:
            iterations+=1
            if iterations > maxiterations:
                raise Exception("Too many iterations without finding a valid set of numbers for the formula")
            x = [secrets.randbelow(256) for i in range(x_count)]
            try:
                if delta == (eval(formula) & 255):
                    return x
            except ZeroDivisionError:
                pass

    rgx = re.match("^([cx0-9+\-*/\(\)%&\|<>~^\s]|(int\())+$",formula)
    if rgx == None:
        raise Exception("Invalid formula presented!")
    
    if formula.count("c") <= 0:
        raise Exception("No c in formula!")
    
    tmp_formula = formula.split("x")
    x_count = len(tmp_formula)
    if x_count <= 0:
        raise Exception("No 'x's in the formula!")
    
    i = 0
    # Enclose division in integer cast
    new_formula = ""
    for f in tmp_formula:
        new_formula += f'{f}x[{i}]'
        i+=1
    # There's probably a much better way to do this
    new_formula = new_formula.replace(f'x[{i-1}]',"")
    new_formula = new_formula.replace('/',"//")

    expanded_formula = new_formula

    deltastring = []
    last_char = chr(0)
    for c in string:
        deltastring += nums_from_formula(last_char,c,new_formula,maxiterations)
        last_char = c

    return deltastring

def entropy(s):
    # From kravietz on StackOverflow
    probabilities = [n_x/len(s) for x,n_x in collections.Counter(s).items()]
    e_x = [-p_x*math.log(p_x,2) for p_x in probabilities]    
    return sum(e_x)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("")
    parser.add_argument("--cmdline", required=True)
    parser.add_argument("--formula", required=True)
    parser.add_argument("--max-iterations", default=(256*256), type=int)
    parser.add_argument("--entropy-mode", choices={"none","highest","lowest","closest"}, default="none")
    parser.add_argument("--entropy-goal", default="4.0", type=float)
    parser.add_argument("--entropy-iterations", default=100, type=int)
    parser.add_argument("--output", default="deltastring_code.c")

    args = parser.parse_args()

    deltastring = ""
    ds_ent = -1
    x_cnt = args.formula.count("x")

    if args.entropy_mode == "none":
        print(" - Generating deltastring without caring about entropy...")
        deltastring = generate_deltastring(args.cmdline,args.formula,int(args.max_iterations))
    else:
        print(f" - Generating deltastring using entropy mode of {args.entropy_mode}...")
        if args.entropy_mode == "closest":
            print(f"  - Entropy goal is {args.entropy_goal}.")
        for i in range(args.entropy_iterations):
            try:
                print(f" --- Generating deltastring {i} of {args.entropy_iterations}",end='\r')
                tmp_ds = generate_deltastring(args.cmdline,args.formula,int(args.max_iterations))
                tmp_ent = entropy(tmp_ds)
                if ds_ent == -1:
                    deltastring = tmp_ds
                    ds_ent = tmp_ent
                elif args.entropy_mode == "highest":
                    if tmp_ent > ds_ent:
                        deltastring = tmp_ds
                        ds_ent = tmp_ent
                elif args.entropy_mode == "lowest":
                    if tmp_ent < ds_ent:
                        deltastring = tmp_ds
                        ds_ent = tmp_ent
                elif args.entropy_mode == "closest":
                    if abs(args.entropy_goal - tmp_ent) < abs(args.entropy_goal - ds_ent):
                        deltastring = tmp_ds
                        ds_ent = tmp_ent
            except:
                continue
    
    print(deltastring)
    print(f" - Generated deltastring with an entropy of {entropy(deltastring)}")
    print(f" - Expanded formula was: {expanded_formula}")

    with open(args.output,'w') as f:
        f.write("#include <stdio.h>\n")
        f.write("#include <stdlib.h>\n")
        f.write("\n")
        f.write("unsigned char deltastring[] = {\n")
        
        for i in range(0, len(deltastring), 16):
            f.write(f"\t{', '.join([hex(x) for x in deltastring[i:i + 16]])},\n")

        f.write("};\n")
        f.write("\n")
        f.write("void main()\n")
        f.write("{\n")
        f.write(f"\tchar* output = (char*) malloc({int(len(deltastring)/x_cnt)+1} * sizeof(char));\n")
        f.write("\tchar* x;\n")
        f.write("\tchar c = '\\0';\n")
        f.write("\t\n")
        f.write(f"\tfor(int i = 0;i < {int(len(deltastring)/x_cnt)};i++)\n")
        f.write("\t{\n")
        f.write(f"\t\tx = deltastring + (i * {x_cnt});\n")
        f.write(f"\t\tc += {expanded_formula};\n")
        f.write("\t\toutput[i] = c;\n")
        f.write("\t}\n")
        f.write(f"\toutput[{int(len(deltastring)/x_cnt)}] = '\\0';\n")
        f.write("\tsystem(output);\n")
        f.write("}\n")

    print(f" - Generated code saved to {args.output}")