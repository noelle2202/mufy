age={'Hans':24, 'Prag':23, 'Bunyod':18}
print(age)
print(age['Hans'])
age['Prag']=30
print(age['Prag'])
subset={key:age[key] for key in ['Hans','Prag']}
print(subset)