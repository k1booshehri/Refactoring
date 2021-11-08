from antlr4.TokenStreamRewriter import TokenStreamRewriter
from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener


class PullFieldRefactoringRemoveListener(JavaParserLabeledListener):
    def __init__(self, common_token_stream_rewriter=None, parent_class_identifier: str = None,
                 child_class_identifier: str = None,
                 filed_identifier: str = None, pull_direction: bool = None):
        self.parent_class_identifier = parent_class_identifier
        self.child_class_identifier = child_class_identifier
        self.field_identifier = filed_identifier
        self.pull_direction = pull_direction

        if common_token_stream_rewriter is not None:
            self.token_stream_rewriter = common_token_stream_rewriter
        else:
            raise TypeError('common_token_stream_rewriter is None')

        self.field_code = None
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

    # Field codes
    def enterMemberDeclaration2(self, ctx: JavaParserLabeled.MemberDeclaration2Context):
        # Pull up direction
        if self.pull_direction:
            variable_declarators = ctx.fieldDeclaration().variableDeclarators().children

            # Single variable declaration
            if 1 == len(variable_declarators):
                # Selected Field
                if self.field_identifier == variable_declarators[0].variableDeclaratorId().IDENTIFIER().getText():
                    # Child class
                    if self.child_class_identifier == self.active_class[-1]:
                        # Set field code
                        self.field_code = self.token_stream_rewriter.getText(
                            program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                            start=ctx.parentCtx.start.tokenIndex,
                            stop=ctx.parentCtx.stop.tokenIndex)

                        self.field_code = '\t' + self.field_code + '\n'

                        # Remove field code
                        self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                          from_idx=ctx.parentCtx.start.tokenIndex,
                                                          to_idx=ctx.parentCtx.stop.tokenIndex)

            # Multiple variable declaration
            if 1 < len(variable_declarators):
                for variable_declarator in variable_declarators:
                    if JavaParserLabeled.VariableDeclaratorContext == type(variable_declarator) \
                            and self.field_identifier == variable_declarator.variableDeclaratorId().IDENTIFIER().getText():
                        # Child class
                        if self.child_class_identifier == self.active_class[-1]:
                            # Set field code
                            self.field_code = self.token_stream_rewriter.getText(
                                program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                start=ctx.parentCtx.start.tokenIndex,
                                stop=ctx.parentCtx.stop.tokenIndex)

                            self.field_code = '\t' + self.field_code + '\n'

                            # Remove field code
                            self.token_stream_rewriter.delete(
                                program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                from_idx=variable_declarator.start.tokenIndex,
                                to_idx=variable_declarator.stop.tokenIndex + 1)

                for variable_declarator in variable_declarators:
                    if JavaParserLabeled.VariableDeclaratorContext == type(variable_declarator) \
                            and not self.field_identifier == variable_declarator.variableDeclaratorId().IDENTIFIER().getText():
                        self.field_code = self.field_code.replace(
                            variable_declarator.variableDeclaratorId().IDENTIFIER().getText(), '')

                self.field_code = self.field_code.replace(',', '')

        # Pull down direction
        if not self.pull_direction:
            variable_declarators = ctx.fieldDeclaration().variableDeclarators().children

            # Single variable declaration
            if 1 == len(variable_declarators):
                # Selected Field
                if self.field_identifier == variable_declarators[0].variableDeclaratorId().IDENTIFIER().getText():
                    # Child class
                    if self.parent_class_identifier == self.active_class[-1]:
                        # Set field code
                        self.field_code = self.token_stream_rewriter.getText(
                            program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                            start=ctx.parentCtx.start.tokenIndex,
                            stop=ctx.parentCtx.stop.tokenIndex)

                        self.field_code = '\t' + self.field_code + '\n'

                        # Remove field code
                        self.token_stream_rewriter.delete(
                            program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                            from_idx=ctx.parentCtx.start.tokenIndex,
                            to_idx=ctx.parentCtx.stop.tokenIndex)

            # Multiple variable declaration
            if 1 < len(variable_declarators):
                for variable_declarator in variable_declarators:
                    if JavaParserLabeled.VariableDeclaratorContext == type(variable_declarator) \
                            and self.field_identifier == variable_declarator.variableDeclaratorId().IDENTIFIER().getText():
                        # Child class
                        if self.parent_class_identifier == self.active_class[-1]:
                            # Set field code
                            self.field_code = self.token_stream_rewriter.getText(
                                program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                start=ctx.parentCtx.start.tokenIndex,
                                stop=ctx.parentCtx.stop.tokenIndex)

                            self.field_code = '\t' + self.field_code + '\n'

                            # Remove field code
                            self.token_stream_rewriter.delete(
                                program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                from_idx=variable_declarator.start.tokenIndex,
                                to_idx=variable_declarator.stop.tokenIndex + 1)
                # Edit field code
                for variable_declarator in variable_declarators:
                    if JavaParserLabeled.VariableDeclaratorContext == type(variable_declarator) \
                            and not self.field_identifier == variable_declarator.variableDeclaratorId().IDENTIFIER().getText():
                        self.field_code = self.field_code.replace(
                            variable_declarator.variableDeclaratorId().IDENTIFIER().getText(), '')

                self.field_code = self.field_code.replace(',', '')

    # Method calls
    def enterExpression21(self, ctx:JavaParserLabeled.Expression21Context):
        # Pull down direction
        if not self.pull_direction:
            # Selected field
            if self.field_identifier == ctx.children[0].IDENTIFIER().getText():
                # Method call has 'super.'
                if 'super' == ctx.children[0].expression().primary().children[0].getText():
                    # Child Class
                    if self.child_class_identifier == self.active_class[-1]:
                        # Remove 'super.'
                        self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                          from_idx=ctx.children[0].expression().start.tokenIndex,
                                                          to_idx=ctx.children[0].expression().stop.tokenIndex + 1)

                # Parent type
                variable_identifier = ctx.children[0].expression().primary().children[0].getText()
                if variable_identifier in self.variables_type \
                        and self.parent_class_identifier == self.variables_type[variable_identifier]:
                    # Remove fields
                    self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                      from_idx=ctx.parentCtx.parentCtx.start.tokenIndex,
                                                      to_idx=ctx.parentCtx.parentCtx.stop.tokenIndex)


class PullFieldRefactoringInsertListener(JavaParserLabeledListener):
    def __init__(self, common_token_stream_rewriter=None, parent_class_identifier: str = None,
                 child_class_identifier: str = None, field_identifier: str = None,
                 field_code: str = None, pull_direction: bool = None):
        self.parent_class_identifier = parent_class_identifier
        self.child_class_identifier = child_class_identifier
        self.field_identifier = field_identifier
        self.field_code = field_code
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
                if self.field_code is not None:
                    # Insert method code
                    self.token_stream_rewriter.insertAfter(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                           index=ctx.stop.tokenIndex - 1,
                                                           text=self.field_code)

        # Pull down direction
        if not self.pull_direction:
            # Child class
            if self.child_class_identifier == self.active_class[-1]:
                # Method code must have a value
                if self.field_code is not None:
                    # Insert method code
                    self.token_stream_rewriter.insertAfter(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                           index=ctx.stop.tokenIndex - 1,
                                                           text=self.field_code)

        self.active_class.remove(ctx.IDENTIFIER().getText())

    def enterExpression0(self, ctx: JavaParserLabeled.Expression0Context):
        # Pull up direction
        if self.pull_direction:
            # Child Class
            if self.child_class_identifier == self.active_class[-1]:
                # Selected method
                if self.field_identifier == ctx.primary().getText():
                    # Insert 'super.'
                    self.token_stream_rewriter.insertAfter(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                           index=ctx.start.tokenIndex - 1,
                                                           text='super.')
