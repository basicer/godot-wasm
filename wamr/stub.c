#include <unistd.h>

#include "bh_log.h"

static uint32 log_verbose_level = BH_LOG_LEVEL_FATAL;

void
bh_log_set_verbose_level(uint32 level)
{
    log_verbose_level = level;
}

void
bh_log(LogLevel log_level, const char *file, int line, const char *fmt, ...)
{
    va_list ap;

    if ((uint32)log_level > log_verbose_level)
        return;

    if (file)
        os_printf("%s, line %d, ", file, line);

    va_start(ap, fmt);
    os_vprintf(fmt, ap);
    va_end(ap);

    os_printf("\n");
}
