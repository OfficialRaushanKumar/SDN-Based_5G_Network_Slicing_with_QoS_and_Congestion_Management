"""Map a configured slice and direction to its expected IPv4 flow tuple."""


def classify_pair(src_ip, dst_ip, hosts, slices):
    for item in slices:
        a, b = item["src_host"], item["dst_host"]
        if (src_ip, dst_ip) in ((hosts[a]["ip"], hosts[b]["ip"]), (hosts[b]["ip"], hosts[a]["ip"])):
            return item
    return None
