package com.digitalbanking.ops.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class OpsStatsResponse {
    private long open;
    private long underInvestigation;
    private long awaitingReview;
    private long resolved;
    private long escalated;
    private long rejected;
    private long totalActive;
}
