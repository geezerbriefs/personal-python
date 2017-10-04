import pyperclip as pyp

print ('Please input your copied file path: ')
text = input()

fixed = text.replace('\\', '/')

pyp.copy(fixed)

print ('Your python compatible file path has been copied to the clipboard')
