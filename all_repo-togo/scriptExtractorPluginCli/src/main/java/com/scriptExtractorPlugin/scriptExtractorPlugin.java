package com.scriptExtractorPlugin;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.application.ApplicationStarter;
import com.intellij.openapi.project.ProjectManager;
import com.intellij.openapi.vfs.LocalFileSystem;
import com.intellij.openapi.vfs.VirtualFile;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiFile;
import com.intellij.psi.PsiManager;
import com.intellij.psi.util.PsiTreeUtil;
import org.jdom.JDOMException;
import org.jetbrains.annotations.Contract;
import org.jetbrains.annotations.NonNls;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import java.io.*;
import java.util.Collection;
import java.util.List;

public class scriptExtractorPlugin implements ApplicationStarter
{

    @Override
    public @NonNls String getCommandName() {
        return "scriptExtractorPlugin";
    }

    @Override
    public void main(@NotNull List<String> args)
    {
        if (args.size() != 4){
            System.out.println("Incorrect command line arguments");
            System.exit(0);
        }
        String projectDirectory = args.get(1);
        String fileName = args.get(2);
        String outputFileDirectory = args.get(3);
        ApplicationStarter.super.main(args);
        String fullPath = projectDirectory + fileName;
        System.out.println("projectDirectory = " + projectDirectory);
        System.out.println("fullPath = " + fullPath);
        System.out.println("outputFileDirectory = " + outputFileDirectory);
        File myFile = new File(fullPath);
        VirtualFile myVirtualFile = LocalFileSystem.getInstance().findFileByIoFile(myFile);
        @Nullable Project project = null;
        try {
            project = ProjectManager.getInstance().loadAndOpenProject(projectDirectory);
        } catch (IOException | JDOMException e) {
            e.printStackTrace();
        }
        assert project != null;
        assert myVirtualFile != null;
        @Nullable PsiFile psiFile = PsiManager.getInstance(project).findFile(myVirtualFile);
        System.out.println("virtual file = " + myVirtualFile);
        System.out.println("project = " + project);
        System.out.println("psiFile = " + psiFile);
        @NotNull Collection<PsiElement> elementList = PsiTreeUtil.findChildrenOfType(psiFile, PsiElement.class);
        String currentFunctionMethodName = null;
        String currentClassName = null;
        int currentMode = 0; // mode 0 = global, mode 1 = function, mode 2 = class
        int oldMode = 0;
        BufferedWriter bw = null;
        String printContent;
        boolean isPrintableFunction = false;
        boolean isPrintableMethod = false;
        try
        {
            bw = buildBufferWriter(outputFileDirectory);
        }
        catch (IOException ex)
        {
            ex.printStackTrace();
        }
        for (PsiElement element : elementList)
        {
            String root = findRoot(element, psiFile);
            String elementType = findElementType(element);
            switch (elementType)
            {
                case "name":
                    printContent = null;
                    if (element.getParent().toString().contains("PyClass:"))
                    {
                        printContent = "Class Name " + element.getText();
                        currentClassName = element.getText();
                        currentMode = 2;
                    }
                    else if (element.getParent().getParent().getParent().toString().contains("PyClass:"))
                    {
                        printContent = "Method Name: " + element.getText() + " class name = " + currentClassName;
                        currentFunctionMethodName = element.getText();
                        isPrintableMethod = true;
                        currentMode = 2;
                    }
                    else if (!element.getParent().toString().contains("PyTargetExpression:"))
                    {
                        printContent = "Function Name: " + element.getText();
                        currentFunctionMethodName = element.getText();
                        isPrintableFunction = true;
                        currentMode = 1;
                        currentClassName = null;
                    }
                    if (isPrintableFunction) {
                        printResult(bw, printContent, true, false, true);
                    }
                    else if (isPrintableMethod)
                    {
                        printResult(bw, printContent, false, true, true);
                    }
                    else
                    {
                        printResult(bw, printContent, oldMode != currentMode, false, true);
                    }
                    oldMode = currentMode;
                    isPrintableFunction = false;
                    isPrintableMethod = false;
                    break;
                case "functionParameter":
                    printContent = null;
                    if (currentMode == 1)
                    {
                        printContent = "Function declaration parameter list = " + element.getText() + " which belongs to the function: " + currentFunctionMethodName;
                    }
                    else if (currentMode == 2)
                    {
                        printContent = "Function declaration parameter list = " + element.getText() + " which belongs to the method: " + currentFunctionMethodName + " of class: " + currentClassName;
                    }
                    printResult(bw, printContent, false, false, false);
                    break;
                case "singleStatement":
                    printContent = null;
                    assert psiFile != null;
                    if (element.getParent().getParent().toString().contains(psiFile.toString()) || root.equals(psiFile.toString()))
                    {
                        printContent = "This single statement " + element.getText() + " is a single global statement";
                        currentMode = 0;
                    }
                    else
                    {
                        if (currentMode == 2)
                        {
                            printContent = "This single statement " + element.getText() + " belongs to method: " + currentFunctionMethodName + " of class: " + currentClassName;
                        }
                        else if (currentMode == 1)
                        {
                            printContent = "This single statement " + element.getText() + " belongs to function: " + currentFunctionMethodName;
                        }
                    }
                    printResult(bw, printContent, currentMode != oldMode, false, true);
                    oldMode = currentMode;
                    break;
                case "callArgument":
                    printContent = null;
                    String argument_list_str = element.getText();
                    if (!argument_list_str.equals(""))
                    {
                        assert psiFile != null;
                        if (root.equals(psiFile.toString())) {
                            printContent = "This argument list is " + element.getText() + " which belongs to the global statement : " + element.getParent().getText();
                        } else {
                            if (currentMode == 1) {
                                printContent = "This argument list is " + element.getText() + " which belongs to the call in line: " + element.getParent().getText() + " of function " + currentFunctionMethodName;
                            } else if (currentMode == 2) {
                                printContent = "This argument list is " + element.getText() + " which belongs to the call in line: " + element.getParent().getText() + " of method " + currentFunctionMethodName + " class " + currentClassName;
                            }
                        }
                    }
                    printResult(bw, printContent, false, false, false);
                    break;

            }

        }
        try
        {
            assert bw != null;
            bw.flush();
            bw.close();
        }
        catch (IOException ex)
        {
            ex.printStackTrace();
        }
        System.exit(0);
    }

    private void printResult(BufferedWriter bw, String printContent, boolean isNewStart, boolean isNewMethod, boolean isNewStatement) {
        if (printContent != null)
        {
            try {
                assert bw != null;
                writeContent(bw, printContent, isNewStart, isNewMethod, isNewStatement);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
//            System.out.println(printContent);
//            System.out.println("============================>");
        }
    }

    private @NotNull String findElementType(@NotNull PsiElement element) {
        if (element.toString().equals("PsiElement(Py:IDENTIFIER)") && !element.getParent().toString().contains("PyNamedParameter(") && !element.getParent().toString().contains("PyReferenceExpression"))
        {
            return "name";
        }
        else if (element.toString().equals("PyParameterList"))
        {
            return "functionParameter";
        }
        else if (element.toString().contains("PyCallExpression"))
        {
            return "singleStatement";
        }
        else if (element.toString().equals("PyArgumentList"))
        {
            return "callArgument";
        }
        return "invalid";
    }

    private String findRoot(PsiElement element, PsiFile psiFile) {
        if (isDesiredParent(element, psiFile))
        {
            return element.toString();
        }
        do
        {
            element = element.getParent();
        }
        while(!isDesiredParent(element, psiFile));
        return element.toString();
    }

    private boolean isDesiredParent(@NotNull PsiElement element, PsiFile psiFile) {
        if (element.toString().contains("PyClass:"))
        {
            return true;
        }
        else if (element.toString().contains("PyFunction("))
        {
            return true;
        }
        else return (element.toString().contains(psiFile.toString()) || element.toString().equals(psiFile.toString()));
    }

    @Contract(" -> new")
    private @NotNull BufferedWriter buildBufferWriter(String outputFileDirectory) throws IOException
    {
        File myResultFile = new File(outputFileDirectory);
        if (myResultFile.createNewFile())
        {
            System.out.println("File Created");
        }
        else
        {
            System.out.println("File existed");
        }
        FileOutputStream fos = new FileOutputStream(myResultFile);
        return new BufferedWriter((new OutputStreamWriter(fos)));
    }

    public void writeContent(BufferedWriter bw, String print_content, boolean isPrintFunction, boolean isPrintMethod, boolean isNewStatement) throws IOException {
        if (isPrintFunction)
        {
            bw.write("**************************>\n");
            bw.write("=========================>");
            bw.newLine();
        }
        if (isPrintMethod)
        {
            bw.write("**************************>\n");
            bw.write("++++++++++++++++++++++++++>");
            bw.newLine();
        }
        if (isNewStatement)
        {
            bw.write("**************************>");
            bw.newLine();
        }

        bw.write(print_content);
        bw.newLine();
    }


}
