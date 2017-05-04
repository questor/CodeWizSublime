import sublime
import sublime_plugin
import re
import os

class CppImplementMethodBuffer:
   returnType = []
   methodName = []
   methodParameter = []
   className = []

gMethodBuffer = CppImplementMethodBuffer

class CodeWizSublimeMethodCopy(sublime_plugin.TextCommand):
   def run(self, edit):
      self.view.run_command('copy')
      text = sublime.get_clipboard()
      if re.match(r'^$|\s+', text): 
         text.strip()

      gMethodBuffer.returnType = []
      gMethodBuffer.methodName = []
      gMethodBuffer.methodParameter = []
      gMethodBuffer.className = []

      for currentline in text.splitlines():
         # get class name
         sel = self.view.sel()[0]
         class_regions = self.view.find_by_selector('entity.name.class')
         method_class = ""
         class_regions = self.view.find_by_selector('entity.name.class')
         found = False
         for r in reversed(class_regions):
            if r.a <= sel.a:
               method_class += self.view.substr(r)
               found = True
               break;

         if found:
            if currentline:
               method_pattern = re.compile(r"(.*)\s+(.*)\s*(\(.*\))")
               match = method_pattern.match(currentline)
               if match:
                  return_type = match.group(1)
                  return_type = return_type.split(" ")
                  return_type = " ".join(return_type).strip()
                  method_name = match.group(2)
                  params = match.group(3)

                  gMethodBuffer.returnType.append(return_type)
                  gMethodBuffer.methodName.append(method_name)
                  gMethodBuffer.methodParameter.append(params)
                  gMethodBuffer.className.append(method_class)
                  #print("append to global list %s %s %s %s" % (method_class, return_type, method_name, params))

class CodeWizSublimeMethodPaste(sublime_plugin.TextCommand):
   def run(self, edit):
      filepath = self.view.file_name()
      if filepath is None:
         print("CodeWizSublime: create file first before using paste method")
         return

      currentlyInHeaderFile = True
      if filepath.find('.h') == -1:
         currentlyInHeaderFile = False

      for i in range(0, len(gMethodBuffer.returnType)):
         return_type = str(gMethodBuffer.returnType[i])
         method_name = gMethodBuffer.methodName[i]
         params = gMethodBuffer.methodParameter[i]
         method_class = gMethodBuffer.className[i]

         if currentlyInHeaderFile:
            return_type = return_type.replace('/*virtual*/', 'virtual')
            return_type = return_type.replace('/*static*/', 'static')
            method_implement_code = "\n\t{return_type} {method_name}{params};".format(
               return_type = return_type,
               method_name = method_name,
               params = params)
         else:
            return_type = return_type.replace('virtual', '/*virtual*/')
            return_type = return_type.replace('static', '/*static*/')
            method_implement_code = "\n{return_type} {class_name}::{method_name}{params} {{\n}}\n".format(
               return_type = return_type,
               class_name = method_class,
               method_name = method_name,
               params = params)

         #print("method_implement_code = %s" % method_implement_code)
         self.view.insert(edit, self.view.sel()[0].begin(), method_implement_code)

class CodeWizSublimeFindFriendMethod(sublime_plugin.TextCommand):
   def run(self, edit):
      filepath = self.view.file_name()
      if filepath is None:
         print("CodeWizSublime: create file first before using paste method")
         return

      currentlyInHeaderFile = True
      if filepath.find('.h') == -1:
         currentlyInHeaderFile = False

      currentLine = self.view.substr(self.view.line(self.view.sel()[0]))
      if currentLine:
         target = ""
         if currentlyInHeaderFile:
            # were in the header, try to find classname by using the selector
            sel = self.view.sel()[0]
            class_regions = self.view.find_by_selector('entity.name.class')
            method_class = ""
            class_regions = self.view.find_by_selector('entity.name.class')
            found = False
            for r in reversed(class_regions):
               if r.a <= sel.a:
                  method_class += self.view.substr(r)
                  found = True
                  break;

            if found:
               method_pattern = re.compile(r"(.*)\s+(.*)\s*(\(.*\))")
               match = method_pattern.match(currentLine)
               if match:
                  return_type = match.group(1)
                  return_type = return_type.split(" ")
                  return_type = " ".join(return_type).strip()
                  method_name = match.group(2)
                  params = match.group(3)

                  target = method_class+"::"+method_name
         else:
            # were in the implementation, try to find classname in the current line
            method_pattern = re.compile(r"(.*)\s+(.*)([:]{2})+(.*)\s*(\(.*\))")
            match = method_pattern.match(currentLine)
            if match:
               return_type = match.group(1)
               return_type = return_type.split(" ")
               return_type = " ".join(return_type).strip()
               class_name = match.group(2)
               method_name = match.group(4)
               params = match.group(5)

               target = method_name

         if currentlyInHeaderFile:
            cppfilepath = filepath.replace(".h", ".cpp")
         else:
            cppfilepath = filepath.replace(".cpp", ".h")

         cpp_view = sublime.active_window().open_file(cppfilepath)

         #print("search for %s" % target)

         content = cpp_view.substr(sublime.Region(0, cpp_view.size()))
         begin = content.find(target)
         if begin == -1:
            return
         cpp_view.show_at_center(begin)
         cpp_view.sel().clear()
         cpp_view.sel().add(sublime.Region(begin))


