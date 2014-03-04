// Trying out making a standalone parser in ANTLR
// Aaron Kane

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import org.antlr.v4.runtime.tree.gui.*;
import org.antlr.v4.runtime.misc.Utils;
import org.antlr.v4.runtime.misc.*;
//import org.antlr.v4.runtime.ANTLRFileStream;
//import org.antlr.v4.runtime.CommonTokenStream;
//import org.antlr.v4.runtime.ParserRuleContext;
//import org.antlr.v4.runtime.Token;
import java.util.List;
import java.util.Arrays;

public class MonTranslate {

	public static void main(String args[]) throws Exception  {
		//ANTLRFileStream in = new ANTLRFileStream(args[0]);
		ANTLRInputStream in = new ANTLRInputStream(System.in);
		MonLogicV2Lexer lex = new MonLogicV2Lexer(in);
		CommonTokenStream tokens = new CommonTokenStream(lex);
		MonLogicV2Parser parser = new MonLogicV2Parser(tokens);
		//parser.setBuildParseTree(true);
		//MonListener listener = new MonListener();
		//parse.addParseListener(listener);
		ParseTree tree = parser.exp();

		ParseTreeWalker walker = new ParseTreeWalker();
		//walker.walk(new MonListener(), tree);
		//System.out.println("");
		//System.out.println("And the tree, just for comparison:");
		System.out.print(tree.toStringTree(parser));
		//System.out.println("And our tree...");
		//System.out.println(toStringTree(tree, parser));

	}

public static String toStringTree(@NotNull Tree t, @Nullable Parser recog) {
		String[] ruleNames = recog != null ? recog.getRuleNames() : null;
		List<String> ruleNamesList = ruleNames != null ? Arrays.asList(ruleNames) : null;
		return toStringTree(t, ruleNamesList);
	}
public static String toStringTree(@NotNull Tree t, @Nullable List<String> ruleNames) {
			String s = Utils.escapeWhitespace(getNodeText(t, ruleNames), false);
			if ( t.getChildCount()==0 ) return s;
			StringBuilder buf = new StringBuilder();
			System.out.println("for s=" + s + "|| child# is " + t.getChildCount());
			if ( t.getChildCount() != 1 || s.equals("exp") || s.equals("prop")) {
				buf.append("[");
				s = Utils.escapeWhitespace(getNodeText(t, ruleNames), false);
				buf.append(s);
				buf.append(' ');
				for (int i = 0; i<t.getChildCount(); i++) {
					if ( i>0 ) buf.append(", ");
					buf.append(toStringTree(t.getChild(i), ruleNames));
				}
				buf.append("]");
			} else {
				for (int i = 0; i<t.getChildCount(); i++) {
					if ( i>0 ) buf.append(", ");
					buf.append(toStringTree(t.getChild(i), ruleNames));
				}
			}
			return buf.toString();
}
public static String getNodeText(@NotNull Tree t, @Nullable List<String> ruleNames) {
		if ( ruleNames!=null ) {
			if ( t instanceof RuleNode ) {
				int ruleIndex = ((RuleNode)t).getRuleContext().getRuleIndex();
				String ruleName = ruleNames.get(ruleIndex);
				return ruleName;
			}
			else if ( t instanceof ErrorNode) {
				return t.toString();
			}
			else if ( t instanceof TerminalNode) {
				Token symbol = ((TerminalNode)t).getSymbol();
				if (symbol != null) {
					String s = symbol.getText();
					return s;
				}
			}
		}
		// no recog for rule names
		Object payload = t.getPayload();
		if ( payload instanceof Token ) {
			return ((Token)payload).getText();
		}
		return t.getPayload().toString();
	}
}
