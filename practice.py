s="iloveleetcode"
c="e"

pos=[]
for a,b in enumerate(s):
    #print(a)
    if b == c:
        pos.append(a)

r = []
for i in range(len(s)):
    print([abs(t - i) for t in pos])