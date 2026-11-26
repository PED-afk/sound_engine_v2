

def encode(text):
    a=' abcdefghijklmnopqrstuvwxyz.!?,"0123456789'
    letters=[]
    for letter in a:
        letters.append(letter)
    
    line=""
    for letter in text:
        if letters.index(letter.lower())<10:
            line+="0"+str(letters.index(letter.lower()))+" "
        else:
            line+=str(letters.index(letter.lower()))+" "
    return line

def decode(numbers):
    a=' abcdefghijklmnopqrstuvwxyz.!?,"0123456789'
    text=""
    for number in numbers:
        intNumber=int(number)
        text+=a[intNumber]
    return text
