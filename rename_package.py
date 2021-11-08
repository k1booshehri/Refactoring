from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener


class RenamePackageRefactoringListener(JavaParserLabeledListener):
    def __init__(self, common_token_stream_rewriter=None, package_name: str = None, new_package_name: str = None):
        self.package_name = package_name
        self.new_package_name = new_package_name

        if common_token_stream_rewriter is not None:
            self.token_stream_rewriter = common_token_stream_rewriter
        else:
            raise TypeError('common_token_stream_rewriter is None')

    def enterPackageDeclaration(self, ctx: JavaParserLabeled.PackageDeclarationContext):
        if self.package_name == ctx.qualifiedName().getText():
            self.token_stream_rewriter.replaceRange(
                from_idx=ctx.qualifiedName().start.tokenIndex,
                to_idx=ctx.qualifiedName().stop.tokenIndex,
                text=self.new_package_name)

    def enterImportDeclaration(self, ctx: JavaParserLabeled.ImportDeclarationContext):
        if self.package_name == ctx.qualifiedName().getText():
            self.token_stream_rewriter.replaceRange(
                from_idx=ctx.qualifiedName().start.tokenIndex,
                to_idx=ctx.qualifiedName().stop.tokenIndex,
                text=self.new_package_name)
