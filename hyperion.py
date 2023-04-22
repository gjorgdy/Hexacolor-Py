
while True:
    txt = open('C:\hyperion.txt', 'r')
    
    string = txt.readline(1)
    print(string[:7], end='\r')

    txt.close()