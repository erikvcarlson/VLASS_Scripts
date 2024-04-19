factor_2 = []
factor_3 = []
factor_5 = []
factor_7 = []
for i in range(1,1500):
    factor_2.append(2*i)
    factor_3.append(3*i)
    factor_5.append(5*i)
    factor_7.append(7*i)
    
factor_list = factor_2 + factor_3 + factor_5 + factor_7
factor_list.sort()
#this cannot be odd 

def closest(lst, K):
      
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
      
# To calculate the value K, take the desire cell size (default 0.6 arcseconds) and divide it by your imagesize plus the buffer (1380 arcseconds)
# For example (500+1380)/0.6 = 3133 which should be your value of K. This image size should then be appended to your image parameter list as 
# imsize = [K,K]
# if other than the default cell size is to be used then the user should also append the cell size to the image parameter list for 
# example cell = ['0.4arcsec','0.4arcsec']

K = 3133
print(closest(factor_list, K))
