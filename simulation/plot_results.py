import matplotlib.pyplot as plt


fig = plt.figure()
ax1 = fig.add_subplot(331)
ax2 = fig.add_subplot(332)
ax3 = fig.add_subplot(333)
ax4 = fig.add_subplot(334)
ax5 = fig.add_subplot(335)
ax6 = fig.add_subplot(336)
ax7 = fig.add_subplot(337)
ax8 = fig.add_subplot(338)
ax9 = fig.add_subplot(339)

names = ['OPT', 'LFU', 'LRU', 'LFRU', 'SHLFRU', 'FBR', 'MQ']
data = {1.01: {10: [38, 15, 13, 15, 20, 16, 17], 20: [55, 27, 24, 25, 31, 28, 28], 30: [66, 36, 35, 36, 40, 38, 37]},
        1.20: {10: [56, 45, 34, 36, 48, 40, 45], 20: [70, 56, 48, 51, 57, 53, 54], 30: [78, 63, 58, 58, 65, 62, 63]},
        1.35: {10: [69, 60, 52, 55, 63, 56, 61], 20: [80, 69, 65, 67, 73, 68, 69], 30: [86, 76, 72, 74, 78, 75, 76]}}


def plot_me(values, ax, cols, cache_size, alpha):
    width = 0.20
    ind = range(len(values))
    bars = ax.bar(ind, values, width, color=cols, alpha=0.4)
    patterns = ('--', '+', 'x', '\\', '..', '//', '||')
    # for bar, pattern in zip(bars, patterns):
    #     bar.set_hatch(pattern)
    ax.set_xticks(ind)
    ax.set_xticklabels(names, fontsize=15)
    if ax in [ax1, ax4, ax7]:
        ax.set_ylabel("Hit Ratio", fontsize=17)
    j = 0
    for point in values:
        ax.text(j, point, f'{point}%', rotation=0, fontsize=15,
                ha="center", va="center", bbox=dict(boxstyle="round", facecolor='#FFFFFF', ec='black'))
        j += 1
    if ax in [ax1, ax2, ax3]:
        ax.set_title(fr'$Cache Size  \Rightarrow {cache_size}$', fontsize=18)
    if ax in [ax3, ax6, ax9]:
        ax.xaxis.set_tick_params(labelsize=15)
        # ax.set_ylabel('\n'.join(wrap(f'{no} MECs', 8)), rotation=0, fontsize=15, labelpad=30)
        axx = ax.twinx()
        axx.set_yticklabels([])
        axx.set_yticks([])
        ax.set_ylim(top=85)
        #axx.set_ylabel('\n'.join(wrap(rf'$\alpha_i={alpha}$', 8)), rotation=0, fontsize=15, labelpad=30)
        axx.set_ylabel(rf'$\alpha={alpha}$', rotation=0, fontsize=18, labelpad=40)
    if ax == ax9:
        ax.set_ylim(top=100)


def main():
    axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]
    color = ['r', 'b', 'g', 'm', 'c', 'brown', 'k']
    #zipfs = [1.01, 1.20, 1.35]
    ind = 0
    for zipf in data:
        for cache_size in data[zipf]:
            plot_me(values=data[zipf][cache_size], ax=axs[ind], cols=color, cache_size=cache_size, alpha=zipf)
            ind += 1
    plt.show()


main()
