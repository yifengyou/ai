#!/usr/bin/env python3

from sandlock import Sandbox, Policy

policy = Policy(

fs_readable=["/usr", "/lib", "/etc"],

fs_writable=["/tmp/sandbox"],

net_allow_hosts=["api.anthropic.com"],

)

result = Sandbox(policy).run(["python3", "agent.py"])
print(f"result = {result}")

