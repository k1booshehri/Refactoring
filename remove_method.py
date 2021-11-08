from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener


class RemoveMethodRefactoringListener(JavaParserLabeledListener):
    def __init__(self, common_token_stream_rewriter=None, method_identifier: str = None):
        self.method_identifier = method_identifier

        if common_token_stream_rewriter is not None:
            self.token_stream_rewriter = common_token_stream_rewriter
        else:
            raise TypeError('common_token_stream_rewriter is None')

    def enterMemberDeclaration0(self, ctx: JavaParserLabeled.MemberDeclaration0Context):
        if self.method_identifier == ctx.methodDeclaration().IDENTIFIER().getText():
            self.token_stream_rewriter.delete(
                program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                from_idx=ctx.parentCtx.start.tokenIndex,
                to_idx=ctx.parentCtx.stop.tokenIndex)

    def enterMethodCall0(self, ctx: JavaParserLabeled.MethodCall0Context):
        if self.method_identifier == ctx.IDENTIFIER().getText():
            self.token_stream_rewriter.delete(
                program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                from_idx=ctx.parentCtx.parentCtx.start.tokenIndex,
                to_idx=ctx.parentCtx.parentCtx.stop.tokenIndex)
