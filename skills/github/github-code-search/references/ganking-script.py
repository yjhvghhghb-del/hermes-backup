#!/usr/bin/env python3
"""
GitHub打野脚本 - 批量搜索免费资源
FOFA + Hunter + Quake + Shodan + Censys + GitHub + Tavily

环境变量配置:
  GITHUB_TOKEN=ghp_xxx
  FOFA_EMAIL=xxx@xxx.com + FOFA_KEY=xxx
  SHODAN_KEY=xxx
  CENSYS_API_ID=xxx + CENSYS_API_SECRET=xxx
  HUNTER_API_KEY=xxx
  QUAKE_API_KEY=xxx
  TAVILY_KEY=xxx

输出目录: ~/ganking_results/
"""

import requests
import json
import time
import os
from datetime import datetime

PROXY = {"http": "http://172.19.0.1:7890", "https": "http://172.19.0.1:7890"}

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
FOFA_EMAIL = os.getenv("FOFA_EMAIL", "")
FOFA_KEY = os.getenv("FOFA_KEY", "")
SHODAN_KEY = os.getenv("SHODAN_KEY", "")
CENSYS_API_ID = os.getenv("CENSYS_API_ID", "")
CENSYS_API_SECRET = os.getenv("CENSYS_API_SECRET", "")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
QUAKE_API_KEY = os.getenv("QUAKE_API_KEY", "")
TAVILY_KEY = os.getenv("TAVILY_KEY", "")

SEARCH_QUERIES = [
    "free API key site:github.com",
    "API key filetype:json github",
    "free LLM API github",
    "free API key list open source",
]

OUTPUT_DIR = "/data/data/com.termux/files/home/ganking_results"


def save_result(engines: str, query: str, results: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_DIR}/{engines}_{ts}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"query": query, "results": results, "timestamp": ts}, f, ensure_ascii=False, indent=2)
    print(f"  💾 保存到 {filename}")


def search_github(query: str, max_pages: int = 3):
    if not GITHUB_TOKEN:
        print("  ⏭️  GitHub: 未配置token，跳过")
        return []
    results = []
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    for page in range(1, max_pages + 1):
        try:
            url = f"https://api.github.com/search/code?q={__import__('urllib.parse', fromlist=['quote']).quote(query)}&per_page=30&page={page}"
            resp = requests.get(url, headers=headers, proxies=PROXY, timeout=15)
            if resp.status_code != 200:
                print(f"  ⚠️  GitHub: {resp.status_code}")
                break
            data = resp.json()
            for item in data.get("items", []):
                results.append({
                    "name": item.get("name", ""),
                    "html_url": item.get("html_url", ""),
                    "repository": item.get("repository", {}).get("full_name", ""),
                    "path": item.get("path", ""),
                })
            if "next" not in resp.links:
                break
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ GitHub: {e}")
            break
    print(f"  ✅ GitHub: 找到 {len(results)} 条结果")
    return results


def search_fofa(query: str):
    if not FOFA_EMAIL or not FOFA_KEY:
        print("  ⏭️  FOFA: 未配置key，跳过")
        return []
    results = []
    try:
        import base64
        qbase64 = base64.b64encode(query.encode()).decode()
        url = "https://fofa.info/api/v1/search/all"
        params = {"email": FOFA_EMAIL, "key": FOFA_KEY, "qbase64": qbase64, "size": 100}
        resp = requests.get(url, params=params, proxies=PROXY, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠️  FOFA: {resp.text[:100]}")
            return []
        data = resp.json()
        if isinstance(data, list):
            for item in data:
                if len(item) >= 3:
                    results.append({"host": item[0], "port": item[1], "protocol": item[2]})
        elif "results" in data:
            for item in data["results"]:
                if len(item) >= 3:
                    results.append({"host": item[0], "port": item[1], "protocol": item[2]})
    except Exception as e:
        print(f"  ❌ FOFA: {e}")
    print(f"  ✅ FOFA: 找到 {len(results)} 条结果")
    return results


def search_shodan(query: str):
    if not SHODAN_KEY:
        print("  ⏭️  Shodan: 未配置key，跳过")
        return []
    results = []
    try:
        url = f"https://api.shodan.io/shodan/host/search?key={SHODAN_KEY}&query={__import__('urllib.parse', fromlist=['quote']).quote(query)}&limit=100"
        resp = requests.get(url, proxies=PROXY, timeout=15)
        data = resp.json()
        if "matches" in data:
            for item in data["matches"]:
                results.append({
                    "ip_str": item.get("ip_str", ""),
                    "port": item.get("port", ""),
                    "product": item.get("product", ""),
                    "hostnames": item.get("hostnames", []),
                })
    except Exception as e:
        print(f"  ❌ Shodan: {e}")
    print(f"  ✅ Shodan: 找到 {len(results)} 条结果")
    return results


def search_censys(query: str):
    if not CENSYS_API_ID or not CENSYS_API_SECRET:
        print("  ⏭️  Censys: 未配置key，跳过")
        return []
    results = []
    try:
        url = "https://search.censys.io/api/v1/search"
        params = {"q": query, "resource": "hosts", "per_page": 100}
        resp = requests.get(url, params=params, proxies=PROXY, timeout=15,
                           auth=(CENSYS_API_ID, CENSYS_API_SECRET))
        data = resp.json()
        if "results" in data:
            for item in data["results"]:
                results.append({
                    "ip": item.get("ip", ""),
                    "protocols": item.get("protocols", []),
                    "services": [s.get("product", "") for s in item.get("services", []) if isinstance(s, dict)],
                })
    except Exception as e:
        print(f"  ❌ Censys: {e}")
    print(f"  ✅ Censys: 找到 {len(results)} 条结果")
    return results


def search_hunter(query: str):
    if not HUNTER_API_KEY:
        print("  ⏭️  Hunter: 未配置key，跳过")
        return []
    results = []
    try:
        url = "https://hunter.qianxin.com/openapi/search"
        params = {"api-key": HUNTER_API_KEY, "search": query, "page": 1, "page_size": 100}
        resp = requests.get(url, params=params, proxies=PROXY, timeout=15)
        data = resp.json()
        if data.get("code") == 200 and "data" in data:
            for item in data["data"].get("arr", []):
                results.append({
                    "domain": item.get("domain", ""),
                    "ip": item.get("ip", ""),
                    "port": item.get("port", ""),
                    "web_title": item.get("web_title", ""),
                })
    except Exception as e:
        print(f"  ❌ Hunter: {e}")
    print(f"  ✅ Hunter: 找到 {len(results)} 条结果")
    return results


def search_quake(query: str):
    if not QUAKE_API_KEY:
        print("  ⏭️  Quake: 未配置key，跳过")
        return []
    results = []
    try:
        url = "https://quake.360.cn/api/v1/search"
        headers = {"X-QuakeAPIKey": QUAKE_API_KEY, "Content-Type": "application/json"}
        payload = {"query": query, "size": 100, "start": 0}
        resp = requests.post(url, json=payload, headers=headers, proxies=PROXY, timeout=15)
        data = resp.json()
        if resp.status_code == 200 and "data" in data:
            for item in data["data"].get("items", []):
                results.append({
                    "ip": item.get("ip", ""),
                    "port": item.get("port", ""),
                    "protocol": item.get("protocol", ""),
                    "service": item.get("service", ""),
                })
    except Exception as e:
        print(f"  ❌ Quake: {e}")
    print(f"  ✅ Quake: 找到 {len(results)} 条结果")
    return results


def search_tavily(query: str):
    if not TAVILY_KEY:
        print("  ⏭️  Tavily: 未配置key，跳过")
        return []
    results = []
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_KEY, "query": query, "search_depth": "basic", "max_results": 20}
        resp = requests.post(url, json=payload, proxies=PROXY, timeout=15)
        data = resp.json()
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", "")[:200],
            })
    except Exception as e:
        print(f"  ❌ Tavily: {e}")
    print(f"  ✅ Tavily: 找到 {len(results)} 条结果")
    return results


def main():
    print("=" * 60)
    print("🎯 GitHub打野 - 批量搜索 (FOFA + Hunter + Quake + Shodan + Censys)")
    print("=" * 60)
    all_results = {}
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] 搜索: {query}")
        print("-" * 50)
        results = {
            "github": search_github(query),
            "fofa": search_fofa(query),
            "shodan": search_shodan(query),
            "censys": search_censys(query),
            "hunter": search_hunter(query),
            "quake": search_quake(query),
            "tavily": search_tavily(query),
        }
        total = sum(len(v) for v in results.values())
        if total > 0:
            save_result("all", query, results)
            all_results[query] = results
        time.sleep(2)
    print("\n" + "=" * 60)
    print("📊 搜索汇总")
    print("=" * 60)
    for query, results in all_results.items():
        print(f"\n🔍 {query}")
        for engine, items in results.items():
            if items:
                print(f"   {engine}: {len(items)} 条")
    summary_file = f"{OUTPUT_DIR}/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 汇总已保存: {summary_file}")
    print("\n✅ 打野完成!")


if __name__ == "__main__":
    main()
