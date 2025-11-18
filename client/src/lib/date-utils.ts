import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import localizedFormat from "dayjs/plugin/localizedFormat";

// Extend dayjs with plugins
dayjs.extend(relativeTime);
dayjs.extend(localizedFormat);

/**
 * Formats a date string or Date object to a readable format with date and time
 * Format: "MMM DD, YYYY hh:mm A" (e.g., "Jan 15, 2024 02:30 PM")
 */
export function formatDateTime(date: string | Date): string {
  return dayjs(date).format("MMM DD, YYYY hh:mm A");
}

/**
 * Formats a date string or Date object to a readable format with date, time, and seconds
 * Format: "MMM DD, YYYY hh:mm:ss A" (e.g., "Jan 15, 2024 02:30:45 PM")
 */
export function formatDateTimeWithSeconds(date: string | Date): string {
  return dayjs(date).format("MMM DD, YYYY hh:mm:ss A");
}

/**
 * Formats a date string or Date object to a short date format
 * Format: "MMM DD, YYYY" (e.g., "Jan 15, 2024")
 */
export function formatDate(date: string | Date): string {
  return dayjs(date).format("MMM DD, YYYY");
}

/**
 * Formats a date string or Date object to a time format
 * Format: "hh:mm A" (e.g., "02:30 PM")
 */
export function formatTime(date: string | Date): string {
  return dayjs(date).format("hh:mm A");
}

/**
 * Gets the relative time from now (e.g., "2 hours ago", "in 3 days")
 */
export function formatRelativeTime(date: string | Date): string {
  return dayjs(date).fromNow();
}

/**
 * Checks if a date is valid
 */
export function isValidDate(date: string | Date): boolean {
  return dayjs(date).isValid();
}

/**
 * Gets the difference in days between two dates
 */
export function getDaysDifference(
  date1: string | Date,
  date2: string | Date
): number {
  return dayjs(date1).diff(dayjs(date2), "day");
}

/**
 * Formats a date to ISO string
 */
export function formatISO(date: string | Date): string {
  return dayjs(date).toISOString();
}
