import pyparsing as pp

class Parser(object):
    def __init__(self):
        priority = pp.Combine(pp.Suppress('<') + pp.Word(pp.nums) + pp.Suppress('>'))
        SEPERATOR = pp.Word("!#$%&'()*+,-./:;<=>?@[\]^_`{|}~")
        objName = pp.Combine(pp.Word(pp.alphanums) + pp.ZeroOrMore(SEPERATOR + pp.Word(pp.alphanums)))
        value = (pp.quotedString | objName)
        assgn = pp.Combine(pp.Word(pp.alphas) + "=" + value)
        self.logLine = priority("pri") + pp.OneOrMore(assgn)("fields")

    def parseMsg(self, line):
        dict = {}
        try:
            obj = self.logLine.parseString(line)
            for field in obj.fields:
                kv = field.split('=')
                dict[kv[0]] = kv[1]
        except pp.ParseException as err:
            dict['err'] = err.line
        finally:
            return dict
