#!/usr/bin/env python3
"""Compile-check framework exercises.

Spring Boot snippets are compiled with Maven against Spring Boot 3.5 (Java 21).
Angular snippets are type-checked with the TypeScript compiler against Angular 22.

    python3 content/tools/check_frameworks.py            # both
    python3 content/tools/check_frameworks.py spring     # one of them
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.dirname(HERE)
BUILD = os.path.join(CONTENT, ".build")
sys.path.insert(0, HERE)
sys.path.insert(0, CONTENT)

import build  # noqa: E402
import dsl  # noqa: E402

SPRING_BOOT = "3.5.16"
ANGULAR = "22.3.0"
TYPESCRIPT = "~6.0.0"

POM = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>{SPRING_BOOT}</version>
  </parent>
  <groupId>app.offleet</groupId>
  <artifactId>framework-check</artifactId>
  <version>1.0.0</version>
  <properties><java.version>21</java.version></properties>
  <dependencies>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-cache</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>
  </dependencies>
</project>
"""


def proxy_settings(path):
    url = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    proxies = ""
    if url:
        u = urlparse(url)
        proxies = (f"<proxies><proxy><id>agent</id><active>true</active><protocol>https</protocol>"
                   f"<host>{u.hostname}</host><port>{u.port}</port></proxy></proxies>")
    with open(path, "w") as fh:
        fh.write(f"<settings>{proxies}</settings>")


def pkg_of(pid):
    return re.sub(r"[^a-z0-9]", "_", pid)


def framework_problems(cat):
    return [p for p in dsl.PROBLEMS if p["category"] == cat]


def check_spring():
    root = os.path.join(BUILD, "spring")
    shutil.rmtree(os.path.join(root, "src"), ignore_errors=True)
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "pom.xml"), "w") as fh:
        fh.write(POM)
    proxy_settings(os.path.join(root, "settings.xml"))
    owners = {}
    for p in framework_problems("spring-boot"):
        pkg = pkg_of(p["id"])
        for a in p["approaches"]:
            for f in a.get("files", []):
                if f["lang"] != "java":
                    continue
                kind = "test" if f["name"].endswith("Test.java") else "main"
                d = os.path.join(root, "src", kind, "java", pkg)
                os.makedirs(d, exist_ok=True)
                path = os.path.join(d, f["name"])
                with open(path, "w") as fh:
                    fh.write(f"package {pkg};\n" + f["src"] + "\n")
                owners[os.path.realpath(path)] = p["id"]
    cmd = ["mvn", "-q", "-B", "-s", "settings.xml", "-DskipTests", "test-compile"]
    res = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    out = res.stdout + res.stderr
    errors = [line for line in out.splitlines() if "[ERROR]" in line and ".java" in line]
    for line in errors[:40]:
        print("SPRING", line.replace(root + "/", ""))
    if res.returncode != 0 and not errors:
        print(out[-3000:])
    print(f"spring: {len(owners)} files, {'OK' if res.returncode == 0 else 'FAILED'}")
    return res.returncode == 0


def check_angular():
    root = os.path.join(BUILD, "angular")
    os.makedirs(root, exist_ok=True)
    pkg = {
        "name": "framework-check", "private": True,
        "dependencies": {f"@angular/{m}": ANGULAR for m in ("core", "common", "forms", "router", "platform-browser", "compiler")}
        | {"rxjs": "~7.8.0", "tslib": "^2.6.0", "zone.js": "~0.15.0"},
        "devDependencies": {"typescript": TYPESCRIPT, "@types/jasmine": "^5.1.0"},
    }
    with open(os.path.join(root, "package.json"), "w") as fh:
        json.dump(pkg, fh, indent=2)
    tsconfig = {
        "compilerOptions": {
            "target": "ES2022", "module": "ES2022", "moduleResolution": "bundler", "lib": ["ES2022", "DOM"],
            "strict": True, "noEmit": True, "skipLibCheck": True, "experimentalDecorators": True,
            "useDefineForClassFields": False, "types": ["jasmine"], "noImplicitOverride": True,
        },
        "include": ["src/**/*.ts"],
    }
    with open(os.path.join(root, "tsconfig.json"), "w") as fh:
        json.dump(tsconfig, fh, indent=2)
    if not os.path.isdir(os.path.join(root, "node_modules", "@angular", "core")):
        r = subprocess.run(["npm", "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd=root,
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:])
            return False
    shutil.rmtree(os.path.join(root, "src"), ignore_errors=True)
    count = 0
    for p in framework_problems("angular"):
        d = os.path.join(root, "src", pkg_of(p["id"]))
        os.makedirs(d, exist_ok=True)
        for a in p["approaches"]:
            for f in a.get("files", []):
                if f["lang"] == "typescript":
                    with open(os.path.join(d, f["name"]), "w") as fh:
                        fh.write(f["src"] + "\n")
                    count += 1
    res = subprocess.run(["npx", "tsc", "-p", "tsconfig.json"], cwd=root, capture_output=True, text=True)
    for line in (res.stdout + res.stderr).splitlines()[:40]:
        print("ANGULAR", line)
    print(f"angular: {count} files, {'OK' if res.returncode == 0 else 'FAILED'}")
    return res.returncode == 0


def main():
    which = sys.argv[1:] or ["spring", "angular"]
    build.load_modules({"spring_boot", "angular"})
    rep = build.Report()
    for num, p in enumerate(dsl.PROBLEMS, 1):
        build.prepare(p, num, rep)
    ok = True
    if "spring" in which:
        ok &= check_spring()
    if "angular" in which:
        ok &= check_angular()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
