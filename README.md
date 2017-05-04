
# CodeWizSublime
Sublime Text plugin for C++ programmers

provides some functions available to old versions of visual studio via the codewiz plugin:
- special copy'n'paste: you can select a function in a header file, switch to implementation and paste the methods already with classname and 'virtual' and 'static' commented
- the same can be done with functions in implementation files back to headers
- you can switch from a function name to the declaration of this function/implementation of this function

default key map is:
- ctrl+alt+q: special copy
- ctrl+alt+w: special paste
- alt+shift+o: switch friend method

example.h:
```
class A {
   virtual void funcA();
};
```
in a header file if you select in class A "funcA" and paste in the cpp you will get 
```
/*virtual*/ void A::funcA() { 
}
```
(and if you select this line in the cpp and paste in the header you will again get the original line).

please note: I've looked at many other plugins how to implemente this one, so credits need to go mostly to others, I have only assembled the pieces...

currently known limitations:
- switching between header and implementation only switches between '*.h' and '*.cpp'
- switching between methods (header/implementation) tries to be smart and searches in headerfiles first for "class " and the name of the class and later for the method name, if you declare your classes not with "class" and one space this will not work correctly!