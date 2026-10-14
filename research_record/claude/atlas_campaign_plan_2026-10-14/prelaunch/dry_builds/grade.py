import math, re
def seg(a,b,h1,h2,alg):
    L=b-a
    if abs(h1-h2)<1e-15*max(h1,h2):
        n=max(1,round(L/h1)); return [a+L*i/n for i in range(n+1)]
    if alg=='A':
        r=(L-h1)/(L-h2); n=max(1,round(math.log(h2/h1)/math.log(r))+1)
    elif alg=='B':
        r=(L-h1)/(L-h2); n=max(1,math.ceil(math.log(h2/h1)/math.log(r)-1e-9)+1)
    elif alg=='C':
        r=(L-h1)/(L-h2); n=max(1,int(math.log(h2/h1)/math.log(r))+1)
    # with n fixed, ratio from endpoints, scale to L
    q=(h2/h1)**(1/(n-1)) if n>1 else 1
    w=[h1*q**k for k in range(n)]; s=sum(w); w=[x*L/s for x in w]
    pts=[a]; 
    for x in w: pts.append(pts[-1]+x)
    pts[-1]=b; return pts
def lines(spec,alg):
    out=[spec[0][0]]
    for (a,h1),(b,h2) in zip(spec,spec[1:]):
        out+=seg(a,b,h1,h2,alg)[1:]
    return out
def parse(text,key):
    return [(float(m.group(1)),float(m.group(2))) for m in re.finditer(rf'^{key}\.mesh loc=(\S+) spac=(\S+)',text,re.M)]
