package com.aibid.common.camunda.stub;

import java.io.Serializable;

public class Deployment implements Serializable {
    public Deployment name(String name) { return this; }
    public Deployment addString(String resourceName, String xml) { return this; }
    public Deployment addBytes(String resourceName, byte[] data) { return this; }
    public DeploymentSource upload(String name) { return new DeploymentSource(); }
    public Deployment deploy() { return this; }
    public String getId() { return null; }
}
