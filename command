#!/bin/bash
echo $(xwininfo -tree -root | rg $(xprop -root _NET_ACTIVE_WINDOW | sd '.*#' '')
)
