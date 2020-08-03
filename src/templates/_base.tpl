{% args motor_state='OFF', ssid='' %}

<div class="container">
  <div class="alert alert-danger d-none" id="alert-error" role="alert"></div>
  <h1 class="text-center">Welcome to 300black Anneal8tor</h1>
  <div class="row">
    <div class="col">
      <div class="card">
        <div class="card-header">
          Status
        </div>
        <ul class="list-group list-group-flush">
          <li class="list-group-item">
            <h3>
              Motor is:
              <span id="state" class="font-weight-bold">{{ motor_state }}</span>
            </h3>
          </li>
          <li class="list-group-item">
            <h3>
              Position:
              <span id="position" class="font-weight-bold">
                0
              </span>
            </h3>
          </li>
          <li class="list-group-item">
            <h3>
              Count:
              <span id="count" class="font-weight-bold">0</span>
            </h3>
          </li>
        </ul>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col my-3">
      <div class="card">
        <div class="card-header">
          Tools
        </div>
        <div class="card-body">
          <div class="list-group list-group-flush">
            <li class="list-group-item">
              <div class="input-group mb-3">
                <div class="input-group-prepend">
                  <span class="input-group-text">
                    Set Position
                  </span>
                </div>
                <input
                  type="text"
                  class="form-control"
                  id="posInput"
                  name="pos"
                />
                <div class="input-group-append">
                  <button class="btn btn-outline-secondary" onclick="setPos()">
                    Submit
                  </button>
                </div>
              </div>
            </li>
            <li class="list-group-item">
              <div class="input-group justify-content-between">
                <button onclick="calibrate()" class="btn btn-primary">
                  Calibrate
                </button>
                <div class="d-inline-flex align-items-baseline">
                  <h5 class="pr-3 my-auto">Power</h5>
                  <button id="pwr-toggle" class="btn btn-outline-danger">
                    <svg
                      width="1em"
                      height="1em"
                      viewBox="0 0 16 16"
                      class="bi bi-power"
                      fill="currentColor"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M5.578 4.437a5 5 0 1 0 4.922.044l.5-.866a6 6 0 1 1-5.908-.053l.486.875z"
                      />
                      <path fill-rule="evenodd" d="M7.5 8V1h1v7h-1z" />
                    </svg>
                  </button>
                </div>
              </div>
            </li>
          </div>
        </div>
      </div>
      <div class="fixed-bottom">
        <div class="d-flex">
          <div class="input-group flex-grow justify-content-center">
            <div class="btn-group btn-group-lg flex-grow-1" role="group">
              <button onclick="makeStep(-1)" class="btn btn-secondary">
                <svg
                  width="1em"
                  height="1em"
                  viewBox="0 0 16 16"
                  class="bi bi-arrow-left-circle"
                  fill="currentColor"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"
                  />
                  <path
                    fill-rule="evenodd"
                    d="M8.354 11.354a.5.5 0 0 0 0-.708L5.707 8l2.647-2.646a.5.5 0 1 0-.708-.708l-3 3a.5.5 0 0 0 0 .708l3 3a.5.5 0 0 0 .708 0z"
                  />
                  <path
                    fill-rule="evenodd"
                    d="M11.5 8a.5.5 0 0 0-.5-.5H6a.5.5 0 0 0 0 1h5a.5.5 0 0 0 .5-.5z"
                  />
                </svg>
              </button>
              <button onclick="makeStep(0)" class="btn btn-secondary">
                <svg
                  width="1em"
                  height="1em"
                  viewBox="0 0 16 16"
                  class="bi bi-house-door"
                  fill="currentColor"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    d="M7.646 1.146a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 .146.354v7a.5.5 0 0 1-.5.5H9.5a.5.5 0 0 1-.5-.5v-4H7v4a.5.5 0 0 1-.5.5H2a.5.5 0 0 1-.5-.5v-7a.5.5 0 0 1 .146-.354l6-6zM2.5 7.707V14H6v-4a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 .5.5v4h3.5V7.707L8 2.207l-5.5 5.5z"
                  />
                  <path
                    fill-rule="evenodd"
                    d="M13 2.5V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z"
                  />
                </svg>
              </button>
              <button onclick="makeStep(1)" class="btn btn-secondary">
                <svg
                  width="1em"
                  height="1em"
                  viewBox="0 0 16 16"
                  class="bi bi-arrow-right-circle"
                  fill="currentColor"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"
                  />
                  <path
                    fill-rule="evenodd"
                    d="M7.646 11.354a.5.5 0 0 1 0-.708L10.293 8 7.646 5.354a.5.5 0 1 1 .708-.708l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0z"
                  />
                  <path
                    fill-rule="evenodd"
                    d="M4.5 8a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1H5a.5.5 0 0 1-.5-.5z"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="row mb-3">
    <div class="col my-3">
      <div class="card">
        <div class="card-header">
          Configuration
        </div>
        <div class="card-body">
          <div class="list-group list-group-flush">
            <div class="list-group-item">
              <form onsubmit="return false">
                <div class="form-group">
                  <div class="input-group">
                    <div class="input-group-prepend">
                      <span class="input-group-text">
                        Wifi SSID
                      </span>
                    </div>
                    <input
                      type="text"
                      class="form-control"
                      id="cfg-wifi-ssid"
                      name="ssid"
                      value="{{ ssid }}"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <div class="input-group">
                    <div class="input-group-prepend">
                      <span class="input-group-text">
                        Wifi Pass
                      </span>
                    </div>
                    <input
                      type="password"
                      class="form-control"
                      id="cfg-wifi-pass"
                      name="ssid"
                    />
                  </div>
                </div>
                <button
                  id="cfg-wifi-submit"
                  type="submit"
                  class="btn btn-primary"
                >
                  Update
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="row my-3">
    <div id="alerts" class="col my-3"></div>
  </div>
</div>
