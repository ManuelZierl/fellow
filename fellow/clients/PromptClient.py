import pexpect

class PromptClient:
    PROMPT = "PROMPT> "

    def __init__(self):
        """
        Initializes a new Bash shell subprocess using `pexpect`.
        Sets a custom shell prompt (`PROMPT> `) to identify command boundaries reliably.
        """
        self.proc = pexpect.spawn('/bin/bash', encoding='utf-8', echo=False)
        self.proc.sendline(f"PS1='{self.PROMPT} '")
        self.proc.expect(f"{self.PROMPT} ")

    def run(self, cmd: str) -> str:
        """
        Sends a shell command to the persistent Bash session and returns its output.

        :param cmd: The shell command to execute.
        :return: the output of the command.
        """
        # not sure if the newline is needed
        # cmd = cmd.replace("\n", "\\n")
        # todo: check multiline commands
        self.proc.sendline(cmd)
        self.proc.expect(f"{self.PROMPT} ")
        output = self.proc.before.strip()
        lines = output.splitlines()
        return '\n'.join(lines)
