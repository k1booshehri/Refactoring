from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener


class PullMethodRefactoringRemoveListener(JavaParserLabeledListener):
    def __init__(self, common_token_stream_rewriter=None, parent_class_identifier: str = None,
                 child_class_identifier: str = None,
                 method_identifier: str = None, pull_direction: bool = None):
        self.parent_class_identifier = parent_class_identifier
        self.child_class_identifier = child_class_identifier
        self.method_identifier = method_identifier
        self.pull_direction = pull_direction

        if common_token_stream_rewriter is not None:
            self.token_stream_rewriter = common_token_stream_rewriter
        else:
            raise TypeError('common_token_stream_rewriter is None')

        self.method_code = None
        self.active_class = []
        self.variables_type = {}

    def enterClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        self.active_class.append(ctx.IDENTIFIER().getText())

    def exitClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        self.active_class.remove(ctx.IDENTIFIER().getText())

    def enterLocalVariableDeclaration(self, ctx: JavaParserLabeled.LocalVariableDeclarationContext):
        variables_type = ctx.typeType().classOrInterfaceType().IDENTIFIER()[0].getText()
        variable_declarators = ctx.variableDeclarators().variableDeclarator()
        for variable_declarator in variable_declarators:
            self.variables_type[variable_declarator.variableDeclaratorId().IDENTIFIER().getText()] = variables_type

    # Method codes
    def enterMemberDeclaration0(self, ctx: JavaParserLabeled.MemberDeclaration0Context):
        # Selected method
        if self.method_identifier == ctx.methodDeclaration().IDENTIFIER().getText():
            # Pull up direction
            if self.pull_direction:
                # Child class
                if self.child_class_identifier == self.active_class[-1]:
                    self.method_code = self.token_stream_rewriter.getText(
                        program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                        start=ctx.parentCtx.start.tokenIndex,
                        stop=ctx.parentCtx.stop.tokenIndex)

                    self.method_code = '\t' + self.method_code + '\n'

                    self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                      from_idx=ctx.parentCtx.start.tokenIndex,
                                                      to_idx=ctx.parentCtx.stop.tokenIndex)

            # Pull down direction
            if not self.pull_direction:
                # Parent class
                if self.parent_class_identifier == self.active_class[-1]:
                    self.method_code = self.token_stream_rewriter.getText(
                        program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                        start=ctx.parentCtx.start.tokenIndex,
                        stop=ctx.parentCtx.stop.tokenIndex)

                    self.method_code = '\t' + self.method_code + '\n'

                    self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                      from_idx=ctx.parentCtx.start.tokenIndex,
                                                      to_idx=ctx.parentCtx.stop.tokenIndex)

    # Method calls
    def enterMethodCall0(self, ctx: JavaParserLabeled.MethodCall0Context):
        # Pull down direction
        if not self.pull_direction:
            # Selected method
            if self.method_identifier == ctx.IDENTIFIER().getText():
                # Method call has 'super.'
                if 'super' == ctx.parentCtx.expression().primary().children[0].getText():
                    # Child Class
                    if self.child_class_identifier == self.active_class[-1]:
                        # Remove 'super.'
                        self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                          from_idx=ctx.parentCtx.children[0].start.tokenIndex,
                                                          to_idx=ctx.parentCtx.children[0].stop.tokenIndex + 1)

                # Parent type
                variable_identifier = ctx.parentCtx.expression().primary().children[0].getText()
                if variable_identifier in self.variables_type \
                        and self.parent_class_identifier == self.variables_type[variable_identifier]:
                    # Remove Method Calls
                    self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                      from_idx=ctx.parentCtx.parentCtx.parentCtx.start.tokenIndex,
                                                      to_idx=ctx.parentCtx.parentCtx.parentCtx.stop.tokenIndex)


class PullMethodRefactoringInsertListener(JavaParserLabeledListener):
    def __init__(self, common_token_stream_rewriter=None, parent_class_identifier: str = None,
                 child_class_identifier: str = None, method_identifier: str = None,
                 method_code: str = None, pull_direction: bool = None):
        self.parent_class_identifier = parent_class_identifier
        self.child_class_identifier = child_class_identifier
        self.method_identifier = method_identifier
        self.method_code = method_code
        self.pull_direction = pull_direction

        if common_token_stream_rewriter is not None:
            self.token_stream_rewriter = common_token_stream_rewriter
        else:
            raise TypeError('common_token_stream_rewriter is None')

        self.active_class = []

    def enterClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        self.active_class.append(ctx.IDENTIFIER().getText())

    def exitClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        # Pull up direction
        if self.pull_direction:
            # Parent class
            if self.parent_class_identifier == self.active_class[-1]:
                # Method code must have a value
                if self.method_code is not None:
                    # Insert method code
                    self.token_stream_rewriter.insertAfter(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                           index=ctx.stop.tokenIndex - 1,
                                                           text=self.method_code)

        # Pull down direction
        if not self.pull_direction:
            # Child class
            if self.child_class_identifier == self.active_class[-1]:
                # Method code must have a value
                if self.method_code is not None:
                    # Insert method code
                    self.token_stream_rewriter.insertAfter(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                           index=ctx.stop.tokenIndex - 1,
                                                           text=self.method_code)

        self.active_class.remove(ctx.IDENTIFIER().getText())

    def enterMethodCall0(self, ctx: JavaParserLabeled.MethodCall0Context):
        # Pull up direction
        if self.pull_direction:
            # Child Class
            if self.child_class_identifier == self.active_class[-1]:
                # Selected method
                if self.method_identifier == ctx.IDENTIFIER().getText():
                    # Insert 'super.'
                    self.token_stream_rewriter.insertAfter(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                           index=ctx.start.tokenIndex - 1,
                                                           text='super.')
