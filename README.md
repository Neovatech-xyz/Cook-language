※ Note: I am a Japanese junior high school student. There might be some grammatical or spelling errors in the code or documentation.
Jp:このプロジェクトのコードは、Googleの「Antigravity」を使用して生成されました。
En:The code for this project was generated using Google Antigravity.

1. How to Run
Write your code in a text editor and save it as test.cook.
Open your terminal and cd to the directory containing the file.
Execute the file using the following command:
python cook.py run cook file name equal test.cook
Note: The .cook file must be located within the parent directory of the interpreter.
Confirmed Environments
Windows 10: Home (22H2 / Build 19045.6937)
macOS: Monterey (Compatibility test pending)
Dev Machine: iMac (21.5-inch, Late 2015), Intel Core i5-5575R @ 2.80GHz (4 cores)
2. Syntax Overview
1. Comments
// comment (Ignored by the interpreter)
2. Variables & Constants
Variable: create variable name equal x in 5 (Let x = 5)
Constant: create constant name equal x in 5 (Const x = 5)
3. Output
console.write("hello")
4. Functions
cook
create function name equal hello arguments name equal a :
start
  console.write(a)
end

// Calling the function
hello("world")

5. Control Flow (If / Else If / Else)
cook
fast check if x > 10:
start
  console.write("a")
end

second check else if x > 5:
start
  console.write("b")
end

third check else:
start
  console.write("c")
end

Note: Use not to invert conditions.
6. Loops
cook
repeat this block code i > 5:
start
  console.write("a")
end

7. Increment / Decrement
Supported styles:
i++ / i--
i = i + 1 / i = i - 1
i equal i plus 1 / i equal i minus 1
3. Libraries & Math
To use math functions, include: use library name equal math
Function	Description	Example
sqrt(x)	Square root	sqrt(16) → 4.0
pi	Pi constant	3.14159...
floor(x)	Round down	floor(3.7) → 3
ceil(x)	Round up	ceil(3.2) → 4
abs(x)	Absolute value	abs(-5) → 5
round(x)	Round to nearest	round(3.5) → 4
4. Operators (Example: a=10, b=3)
Operation	Cook Syntax (Alternative)	Result
Addition	a plus b (a + b)	13
Subtraction	a minus b (a - b)	7
Multiplication	a times b (a * b)	30
※Jp:翻訳にはgoogleのAIモードを使用しました
※En:Translation was performed using Google's AI mode.
Division	a divided by b (a / b)	3.333
Modulo	a mod b (a % b)	1
Power	a power b (a ** b)	1000
