# - 
# list0 = [7,7,3,8,5]
# list0.sort()
# print(list0)
# list1 = [[2,7,7],[1,7,3],[2,3,8],[2,8,2],[2,5,9]]
# print(list1)
# list1.sort(key=lambda x: x[0])
# print(list1)


# ip = "5.22.0.0"
# ip_split = ip.split(".")
# for ip in ip_split:
#     bin_ip = bin(ip)
# ip2 = "5.22.127.255"
# ip2_spit = ip2.split(".")

# car = {
#   "brand": "Ford",
#   "model": "Mustang",
#   "year": 1964
# }


# print(car.items())

def zarb(a=2,b):
    return a*b

print("zarb 2* 4 is : ", zarb(4))

l1 = [6,3,7,2,5]
l2=l1.copy()
l2.sort()
print('l2 is : ',l2)
print("l1 is : ",l1)