def analyze_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("Total lines:", len(lines))
    
    # Find lines with percentages
    percent_lines = [line.strip() for line in lines if '%' in line]
    print("\nSample lines with percentages:")
    for line in percent_lines[:10]:
        print(line)
    
    # Find lines with HS codes
    hs_lines = [line.strip() for line in lines if line.strip() and line.strip()[0:2].isdigit()]
    print("\nSample HS code lines:")
    for line in hs_lines[:10]:
        print(line)
    
    # Look for rate sections
    rate_contexts = []
    for i, line in enumerate(lines):
        if 'DUTY RATE' in line or 'duty rate' in line.lower():
            context = lines[max(0, i-5):i+6]
            rate_contexts.append(context)
    
    print("\nSample rate contexts:")
    for context in rate_contexts[:2]:
        print("\nContext:")
        for line in context:
            print(line.strip())

if __name__ == "__main__":
    analyze_file("tarfah.txt")